#include "manage_keeb.h"

int main(void) {
  // program flow would be something like:
  // 1. conf = getConfig(argv[0])
  //    - run checks to ensure proper configuration
  //    - ensure pause / exit keybind exists
  // 2. keeb = selectKeeb()
  //    - run checks to ensure keyboard can perform all keybinds in config
  // 3. gp = createGamepad()
  // 4. translateInputs(keeb) <-> outputGamepadEvents(gp, conf)
  //    - Both should run concurrently
  // 5. exit program when exit keybind pressed

  keeb *keeb_dev = selectKeeb();

  return 0;
}
