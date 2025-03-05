# for Super Smash Bros. Melee

import sys
import time
import random
import math

import evdev
import uinput


# edit these to change keybinds
ACTIVATE_Bind = evdev.ecodes.KEY_BACKSPACE
MODB_Bind = evdev.ecodes.KEY_X
L_Bind = evdev.ecodes.KEY_SEMICOLON
LEFT_Bind = evdev.ecodes.KEY_S
DOWN_Bind = evdev.ecodes.KEY_D
RIGHT_Bind = evdev.ecodes.KEY_F
MODX_Bind = evdev.ecodes.KEY_A
MODY_Bind = evdev.ecodes.KEY_LEFTALT
START_Bind = evdev.ecodes.KEY_ESC
R_Bind = evdev.ecodes.KEY_U
Y_Bind = evdev.ecodes.KEY_K
LS_Bind = evdev.ecodes.KEY_O
MS_Bind = evdev.ecodes.KEY_P
B_Bind = evdev.ecodes.KEY_M
X_Bind = evdev.ecodes.KEY_I
Z_Bind = evdev.ecodes.KEY_L
UP_Bind = evdev.ecodes.KEY_SPACE
A_Bind = evdev.ecodes.KEY_J
CUP_Bind = evdev.ecodes.KEY_H
CDOWN_Bind = evdev.ecodes.KEY_COMMA
CLEFT_Bind = evdev.ecodes.KEY_N
CRIGHT_Bind = evdev.ecodes.KEY_DOT


def translateInputs(keeb_device):
    with uinput.Device([
        uinput.BTN_GAMEPAD,
        uinput.BTN_START,
        uinput.BTN_0,
        uinput.BTN_1,
        uinput.BTN_2,
        uinput.BTN_3,
        uinput.BTN_WEST,  # dpad left
        uinput.BTN_EAST,  # dpad right
        uinput.BTN_NORTH, # dpad up
        uinput.BTN_SOUTH, # dpad down
        uinput.BTN_TR2,
        uinput.BTN_TL,
        uinput.BTN_TR,
        uinput.ABS_HAT1X + (0, 255, 0, 0), # analog triggers
        uinput.ABS_X  + (-128, 127, 0, 0), # gray stick left/right
        uinput.ABS_Y  + (-128, 127, 0, 0), # gray stick up/down
        uinput.ABS_RX + (-128, 127, 0, 0), # cstick left/right
        uinput.ABS_RY + (-128, 127, 0, 0)  # cstick up/down
    ]) as gamepad_device:
        print("Keyboard device ready, press", evdev.ecodes.KEY[ACTIVATE_Bind], "to ungrab the keyboard.")
        keeb_device.grab()
        active = True
        time.sleep(0.5)

        active_keys = keeb_device.active_keys()
        prev_active_keys = []
        graystick_block_reac = [False, False]
        graystick_target = [0, 0]
        graystick_prev = []
        graystick_current = [0, 0]
        graystick_lerp_start = [0, 0]
        graystick_fuzz = [0, 0]
        graystick_start_time = time.time()
        while True:
            prev_active_keys = active_keys
            active_keys = keeb_device.active_keys()
            active_keys_vals = {}

            for key in prev_active_keys:
                if key not in active_keys: active_keys_vals[key] = 0
            for key in active_keys:
                if key not in prev_active_keys: active_keys_vals[key] = 1
                else: active_keys_vals[key] = 2

            if ACTIVATE_Bind in active_keys and active_keys_vals[ACTIVATE_Bind] == 1:
                if active:
                    print("Keyboard ungrabbed. Use", evdev.ecodes.KEY[ACTIVATE_Bind], "to grab")
                    active = False
                    keeb_device.ungrab()
                    time.sleep(0.5)
                else:
                    print("Keyboard grabbed. Use", evdev.ecodes.KEY[ACTIVATE_Bind], "to ungrab")
                    active = True
                    keeb_device.grab()
                    time.sleep(0.5)
            if not active: continue

            shield_pressed = L_Bind in active_keys or R_Bind in active_keys or LS_Bind in active_keys or MS_Bind in active_keys

            if len(graystick_prev) > 0 and graystick_target != graystick_prev[0][0]:
                graystick_prev.insert(0, (graystick_target, graystick_start_time))
                graystick_lerp_start = graystick_current
            elif len(graystick_prev) == 0:
                graystick_prev = [(graystick_target, graystick_start_time)]
                graystick_lerp_start = graystick_current
            if len(graystick_prev) > 10: graystick_prev = graystick_prev[0:10]
            (graystick_block_reac, graystick_target, graystick_start_time) = grayStickTarget(active_keys, graystick_block_reac, shield_pressed, graystick_prev, graystick_start_time)
            graystick_fuzz = grayStickFuzz(graystick_fuzz, graystick_target, graystick_prev)
            graystick_current = grayStickTravelTime(graystick_fuzz, graystick_current, graystick_target, graystick_prev, graystick_lerp_start, graystick_start_time)

            gamepad_device.emit(uinput.ABS_X, graystick_current[0], syn = False)
            gamepad_device.emit(uinput.ABS_Y, graystick_current[1], syn = True)

            cstick_target = [0, 0]
            if isSublist([MODX_Bind, MODY_Bind], active_keys):
                if CUP_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_NORTH, active_keys_vals[CUP_Bind])
                elif CDOWN_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_SOUTH, active_keys_vals[CDOWN_Bind])
                if CLEFT_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_WEST, active_keys_vals[CLEFT_Bind])
                elif CRIGHT_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_EAST, active_keys_vals[CRIGHT_Bind])
            elif MODX_Bind in active_keys:
                if CLEFT_Bind in active_keys:    cstick_target[0] = -68
                elif CRIGHT_Bind in active_keys: cstick_target[0] = 68
                if CUP_Bind in active_keys:      cstick_target[1] = 42
                elif CDOWN_Bind in active_keys:  cstick_target[1] = -42
            elif MODY_Bind in active_keys:
                if CLEFT_Bind in active_keys:    cstick_target[0] = -42
                elif CRIGHT_Bind in active_keys: cstick_target[0] = 42
                if CUP_Bind in active_keys:      cstick_target[1] = 68
                elif CDOWN_Bind in active_keys:  cstick_target[1] = -68
            else:
                if CLEFT_Bind in active_keys:    cstick_target[0] = -80
                elif CRIGHT_Bind in active_keys: cstick_target[0] = 80
                if CUP_Bind in active_keys:      cstick_target[1] = 80
                elif CDOWN_Bind in active_keys:  cstick_target[1] = -80

                if CDOWN_Bind and CLEFT_Bind:    cstick_target = [-42, -68]
                elif CDOWN_Bind and CRIGHT_Bind: cstick_target = [42, -68]
            gamepad_device.emit(uinput.ABS_RX, cstick_target[0], syn = False)
            gamepad_device.emit(uinput.ABS_RY, cstick_target[1], syn = False)

            analog_trigger_val = 0
            if L_Bind in active_keys_vals.keys():
                gamepad_device.emit(uinput.BTN_TL, active_keys_vals[L_Bind])
                analog_trigger_val = 0
            elif LS_Bind in active_keys: analog_trigger_val = 49
            elif MS_Bind in active_keys: analog_trigger_val = 94

            gamepad_device.emit(uinput.ABS_HAT1X, analog_trigger_val, syn = True)

            if A_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_0, active_keys_vals[A_Bind])
            if B_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_1, active_keys_vals[B_Bind])
            if X_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_2, active_keys_vals[X_Bind])
            if Y_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_3, active_keys_vals[Y_Bind])
            if Z_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_TR2, active_keys_vals[Z_Bind])
            if R_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_TR, active_keys_vals[R_Bind])
            if START_Bind in active_keys_vals.keys(): gamepad_device.emit(uinput.BTN_START, active_keys_vals[START_Bind])


# gray stick functions
def grayStickTarget(active_keys, graystick_block_reac, shield_pressed, graystick_prev, graystick_start_time):
    reac = [graystick_block_reac[0], graystick_block_reac[1]]
    target = [0, 0]

    # SOCD Cleaning: NSOCD no reactivation
    # NSOCD will lock inputs in all axes even if only SOCD in one axis
    if LEFT_Bind not in active_keys and RIGHT_Bind not in active_keys: reac[0] = False
    if UP_Bind not in active_keys and DOWN_Bind not in active_keys:    reac[1] = False

    if not graystick_block_reac[0] and isSublist([LEFT_Bind, RIGHT_Bind], active_keys): reac[0] = True
    if not graystick_block_reac[1] and isSublist([UP_Bind, DOWN_Bind], active_keys): reac[1] = True
    if True in reac: return(reac, target, time.time())

    # actual translation
    dir = [0, 0]
    if LEFT_Bind in active_keys:    dir[0] = -1
    elif RIGHT_Bind in active_keys: dir[0] = 1
    if UP_Bind in active_keys:      dir[1] = 1
    elif DOWN_Bind in active_keys:  dir[1] = -1
    diag = dir[0] != 0 and dir[1] != 0

    if MODX_Bind in active_keys:
        if diag:
            if shield_pressed and MODB_Bind in active_keys: target = [68 * dir[0], 41 * dir[1]] # diag + shield + b
            elif shield_pressed:                            target = [51 * dir[0], 30 * dir[1]] # diag + shield, no b
            elif MODB_Bind in active_keys:
                # diag + b, no shield
                if CUP_Bind in active_keys:      target = [58 * dir[0], 42 * dir[1]]
                elif CDOWN_Bind in active_keys:  target = [70 * dir[0], 31 * dir[1]]
                elif CLEFT_Bind in active_keys:  target = [68 * dir[0], 42 * dir[1]]
                elif CRIGHT_Bind in active_keys: target = [51 * dir[0], 42 * dir[1]]
                else:                            target = [73 * dir[0], 31 * dir[1]]
            else:
                # diag, no shield, no b
                if CUP_Bind in active_keys:      target = [51 * dir[0], 37 * dir[1]]
                elif CDOWN_Bind in active_keys:  target = [56 * dir[0], 25 * dir[1]]
                elif CLEFT_Bind in active_keys:  target = [53 * dir[0], 33 * dir[1]]
                elif CRIGHT_Bind in active_keys: target = [49 * dir[0], 41 * dir[1]]
                else:                            target = [58 * dir[0], 25 * dir[1]]
        else: target = [53 * dir[0], 42 * dir[1]] # cardinals
    elif MODY_Bind in active_keys:
        if diag:
            if shield_pressed:
                if dir[1] == -1:  target = [40 * dir[0], 68 * dir[1]]
                elif dir[1] == 1: target = [38 * dir[0], 70 * dir[1]]
            elif MODB_Bind in active_keys:
                if CUP_Bind in active_keys:      target = [41 * dir[0], 56 * dir[1]]
                elif CDOWN_Bind in active_keys:  target = [29 * dir[0], 56 * dir[1]]
                elif CLEFT_Bind in active_keys:  target = [35 * dir[0], 56 * dir[1]]
                elif CRIGHT_Bind in active_keys: target = [46 * dir[0], 57 * dir[1]]
                else:                            target = [26 * dir[0], 61 * dir[1]]
            else:
                if CUP_Bind in active_keys:      target = [46 * dir[0], 63 * dir[1]]
                elif CDOWN_Bind in active_keys:  target = [37 * dir[0], 70 * dir[1]]
                elif CLEFT_Bind in active_keys:  target = [42 * dir[0], 68 * dir[1]]
                elif CRIGHT_Bind in active_keys: target = [46 * dir[0], 57 * dir[1]]
                else:                            target = [31 * dir[0], 73 * dir[1]]
        else:
            target = [27 * dir[0], 59 * dir[1]] # cardinals
    else:
        if diag:
            if dir[1] == 1:    target = [56 * dir[0], 61]
            elif dir[1] == -1: target = [61 * dir[0], -56]
        else: target = list(map(lambda x: x * 80, dir))

    if len(graystick_prev) > 0 and target == graystick_prev[0][0]: return (reac, target, graystick_start_time)

    # SDI Nerfs / Conditionally Inaccessible Coordinates
    # from https://github.com/CarVac/MeleeConchRuleset/blob/main/ruleset.md#smash-directional-influence-restrictions
    # and right above it as well
    def checkSDI(coord):
        if (abs(coord[0]) >= 56 and abs(coord[1]) < 23) or (abs(coord[0]) < 23 and abs(coord[1]) >= 56):                return "card" # cardinal SDI input
        elif (abs(coord[0] >= 23 and abs(coord[1]) >= 23 and ((coord[0] * coord[0]) + (coord[1] * coord[1])) >= 3136)): return "diag" # diagonal SDI input
        else:                                                                                             return "ntrl" # no SDI input
    def isAdjacent(coord1, coord2):
        # diag -> card
        if (checkSDI(coord1) == "card" and checkSDI(coord2) == "diag" and (
            (coord1[0] >= 56 and coord2[0] > 0) or
            (coord1[0] <= -56 and coord2[0] < 0) or
            (coord1[1] >= 56 and coord2[1] > 0) or
            (coord1[1] <= -56 and coord2[1] < 0))): return True
        # card -> diag
        if (checkSDI(coord1) == "diag" and checkSDI(coord2) == "card" and (
            (coord2[0] >= 56 and coord1[0] > 0) or
            (coord2[0] <= -56 and coord1[0] < 0) or
            (coord2[1] >= 56 and coord1[1] > 0) or
            (coord2[1] <= -56 and coord1[1] < 0))): return True
        # diag -> diag
        if (checkSDI(coord1) == checkSDI(coord2) == "diag" and (
            (coord1[0] > 0 and coord2[0] > 0) or
            (coord1[0] < 0 and coord2[0] < 0) or
            (coord1[1] > 0 and coord2[1] > 0) or
            (coord1[1] < 0 and coord2[1] < 0)
        )): return True

        return False
    if len(graystick_prev) >= 2:
        # SDI Nerfs
        if ((checkSDI(target) and checkSDI(graystick_prev[0][0]) == "ntrl" and checkSDI(graystick_prev[1][0]) != "ntrl" and time.time() - graystick_prev[1][1] < 0.09167) or
            (isAdjacent(target, graystick_prev[0][0]) and isAdjacent(graystick_prev[0][0], graystick_prev[1][0]) and time.time() - graystick_prev[1][1] < 0.09167)):
            return (reac, graystick_prev[0][0], graystick_start_time)

        # dash back nerfs
        if (abs(graystick_prev[0][0][0]) >= 64 and abs(graystick_prev[1][0][0] >= 64) and abs(graystick_prev[0][0][0] + graystick_prev[1][0][0]) >= 128 and graystick_prev[0][1] - graystick_prev[1][1] <= 0.25):
            if (target[1] >= 23 and target[1] <= 52): return(reac, [dir[0] * 59, 53], time.time())
            if (target[1] >= -52 and target[1] <= -23):
                angle = math.atan2(target[1], target[0])
                return(reac, [math.ceil(80 * math.cos(angle)), math.ceil(80 * math.sin(angle))], time.time())

    if len(graystick_prev) >= 1:
        # conditionally inaccessible coordinates
        # (Y < 0) -> (0.2875 < Y < 0.650) in 2 (0.03334 s) frames : results in Y >= 0.6625
        if (graystick_prev[0][0][1] < 0 and target[1] >= 23 and target[1] <= 52): return (reac, [dir[0] * 59, 53], time.time())

    return (reac, target, time.time())
def grayStickFuzz(fuzz, target, prev):
    if len(prev) > 0 and prev[0][0] == target: return fuzz

    new_target = [target[0], target[1]]
    if target[0] != 0:
        ri = random.randint(0, 3)
        if ri == 2:   new_target[0] += 1
        elif ri == 3: new_target[0] -= 1
    if target[1] != 0:
        ri = random.randint(0, 3)
        if ri == 2:   new_target[1] += 1
        elif ri == 3: new_target[1] -= 1
    return new_target
def grayStickTravelTime(fuzz, cur, target, prev, lerp_start, start_time):
    if cur == fuzz: return cur

    cur_ms = math.floor((time.time() - start_time) / 0.001)
    tar_sq = (target[0] * target[0]) + (target[1] * target[1])
    travel_time = 12

    if tar_sq <= 6184: travel_time = 12
    elif tar_sq >= 6185 and tar_sq <= 6857: travel_time = 6
    elif tar_sq >= 6858 and tar_sq <= 8978: travel_time = 7
    elif tar_sq >= 8979: travel_time = 8

    if (cur_ms >= travel_time): return fuzz
    return [
        round(lerp_start[0] + ((fuzz[0] - lerp_start[0]) * (cur_ms / travel_time))),
        round(lerp_start[1] + ((fuzz[1] - lerp_start[1]) * (cur_ms / travel_time)))
    ]


# === DO NOT TOUCH ===
def isSublist(xs, ys):
    for x in xs:
        if x not in ys: return False
    return True


def chooseDevice(err_msg = None):
    print("\n")
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    devices.sort(key=lambda x: (len(x.path), x.path))
    for i, device in enumerate(devices): print(i, "\t", device.path, "\t", device.name)
    print(str(len(devices)) + "\tExit Program")
    if err_msg != None: print(err_msg)
    selection = input("Select keyboard [0-" + str(len(devices)) + "]: ")

    if not selection.isdigit(): chooseDevice("Answer was not an integer.")
    selection = int(selection)
    if selection < -1 or selection > len(devices): chooseDevice("Answer not in range.")
    if selection == len(devices): sys.exit(0)

    return devices[selection]


if __name__ == "__main__":
    try:
        keeb = chooseDevice()
        time.sleep(0.5)
        translateInputs(keeb)
    except KeyboardInterrupt:
        print("\nInterrupted by keyboard.")
        sys.exit(130)
