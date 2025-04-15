// This is a function that prompts the user to select a keyboard. Returns either
// a pointer to the keyboard or NULL if the user decides to exit the program or
// when there is an error.

#include "../include/manage_keeb.h"

#if __linux__

extern "C" {
#include <fcntl.h>
#include <libevdev/libevdev.h>
#include <unistd.h>
}

#include <filesystem>
#include <iostream>
#include <string>

keeb *selectKeeb(void) {
  // TODO(shell): add a list that stores the filepaths for selection later
  int keebs_num = 0;

  std::cout << "0\tExit th0xx\n";
  for (const auto &entry : std::filesystem::directory_iterator("/dev/input")) {
    // get only "/dev/input/event" files
    const std::string FILE_PATH(entry.path());
    if (FILE_PATH.find("/dev/input/event") == std::string::npos)
      continue;

    struct libevdev *dev = NULL;
    int              fd  = open(FILE_PATH.c_str(), O_RDONLY | O_NONBLOCK);
    int              rc  = libevdev_new_from_fd(fd, &dev);
    if (rc != 0)
      continue;

    // a keyboard should have a spacebar, right?
    if (libevdev_has_event_code(dev, EV_KEY, KEY_SPACE) != 1)
      continue;

    keebs_num++;
    std::cout << keebs_num << "\t" << libevdev_get_name(dev) << " ("
              << FILE_PATH << ")" << "\n";

    libevdev_free(dev);
    close(fd);
  }

  // TODO(shell): properly add selecting a keyboard
  std::cout << "\nPlease select your keyboard. [0-" << keebs_num << "] ";

  return nullptr;
}

#endif
