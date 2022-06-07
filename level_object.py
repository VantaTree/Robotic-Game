import pygame
from config import *
import level_object_funcs as lvl_obj_funcs


def create_objects(lvl_no):
    '''
    Creates objects for given level.
    '''
    OBJECTS = set()

    id_ = 0
    while 1:
        try:
            OBJECTS.add(eval(f'lvl_obj_funcs.level_{lvl_no}_id_{id_}()'))
            id_ += 1
        except AttributeError:break


    return OBJECTS