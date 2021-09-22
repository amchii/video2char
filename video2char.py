#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import time
from config import *
import os
import enum


class Platform(enum.IntEnum):
    NT = 1
    POSIX = 2


if os.name == "nt":
    platform = Platform.NT
elif os.name == "posix":
    platform = Platform.POSIX
else:
    platform = Platform.POSIX


def clear_screen():
    if platform == Platform.NT:
        cmd = "cls"
    else:
        cmd = "clear"
    os.system(cmd)


ascii_char = ASCII_CHAR
char_len = len(ascii_char)


def show_image(img, timeout=0):
    cv2.namedWindow("image")
    cv2.imshow("image", img)
    cv2.waitKey(timeout * 1000)
    cv2.destroyAllWindows()


def auto_thumb(img):
    height, width = img.shape[:2]
    if width >= D_WIDTH:
        height = height / (width / D_WIDTH) * 0.5
        width = D_WIDTH
    else:
        height = height / 2
    return cv2.resize(img, (int(width), int(height)))


def to_chars(img, w_thumb=1.0, h_thumb=1.0):
    height, width = img.shape[:2]
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if w_thumb == h_thumb == 1 and AUTO_THUMB is True:
        img_gray_resize = auto_thumb(img_gray)
    else:
        img_gray_resize = cv2.resize(
            img_gray, (int(width / w_thumb), int(height / h_thumb))
        )
    chars = ""
    for row in img_gray_resize:
        for pixel in row:
            chars += ascii_char[int(pixel / 256 * char_len)]
        chars += "\n"
    return chars


def to_chars_print(img, w_thumb=1.0, h_thumb=1.0):
    clear_screen()
    print(to_chars(img, w_thumb=1.0, h_thumb=1.0))


def video2char_sync(file):
    video = cv2.VideoCapture(file)
    if video.isOpened():
        play = input("是否播放同步视频？(y/n)(字符画可能会闪烁,这取决于你的机器)\n:")
        flag, frame = video.read()
        if play.lower() == "y":
            cv2.namedWindow(
                "video", flags=cv2.WINDOW_NORMAL
            )  # flags == WINDOW_AUTOSIZE | WINDOW_KEEPRATIO | WINDOW_GUI_EXPANDED
            while flag:
                to_chars_print(frame, VIDEO_W_THUMB, VIDEO_H_THUMB)
                cv2.imshow("video", frame)
                cv2.waitKey(1)
                time.sleep(VIDEO_FLASH_TIME)
                flag, frame = video.read()
        else:
            while flag:
                to_chars_print(frame, VIDEO_W_THUMB, VIDEO_H_THUMB)
                time.sleep(VIDEO_FLASH_TIME)
                flag, frame = video.read()
        cv2.destroyAllWindows()

    else:
        print("非支持的文件...")
        exit(1)


def video2char_async(file):
    """
    先加载完再打印
    """
    video = cv2.VideoCapture(file)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"fps: {fps}, frame count: {frame_count}")
    char_frames = []

    if video.isOpened():
        flag, frame = video.read()
        i = 1
        while flag:
            print(f"{i}/{frame_count}", end="\r", flush=True)
            char_frames.append(to_chars(frame))
            i += 1
            flag, frame = video.read()

    else:
        print("非支持的文件...")
        exit(1)

    for char_frame in char_frames:
        clear_screen()
        print(char_frame)
        time.sleep(1 / fps)


if __name__ == "__main__":
    print(
        "------------建议按分辨率将宽度缩小至百级像素,高缩小倍数为宽2倍,缩小控制台输出字体效果更佳(默认宽度为%s)-------------"
        % D_WIDTH
    )
    print("当前路径：%s" % os.path.abspath("."))
    while True:
        file_path = input("请输入图片或视频路径：")
        if os.path.isfile(file_path):
            break
        print("路径错误:目标不是文件")

    img = cv2.imread(file_path)
    if img is not None:
        print("当前图片尺寸为宽：%s 高：%s" % (img.shape[1], img.shape[0]))
        show_image(img, 1)
        flag = input("是否手动缩小比例(Y/n)?\n:")
        if flag.lower() == "y":
            print("缩小倍数：")
            w_thumb = float(input("宽："))
            h_thumb = float(input("高："))
            to_chars_print(img, w_thumb, h_thumb)
        else:
            to_chars_print(img)
    else:
        print("文件非图片,尝试打开为视频...")
        sync = input("请选择模式：\n\t加载时打印：1\n\t加载完打印：2\n:")
        if sync == "1":
            video2char_sync(file_path)
        elif sync == "2":
            video2char_async(file_path)
