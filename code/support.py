import os
import sys
import pygame
from os import walk

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def import_folder(path):
    surface_list = []
    absolute_path = resource_path(path)

    for _, __, img_files in walk(absolute_path):
        for image in img_files:
            full_path = os.path.join(absolute_path, image)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list