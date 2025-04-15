#ifndef MANAGE_KEEB_H
#define MANAGE_KEEB_H

#if __linux__

#define keeb struct libevdev

#endif

keeb *selectKeeb(void);

#endif // MANAGE_KEEB_H
