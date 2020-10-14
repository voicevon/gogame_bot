
import sys
sys.path.append('/home/xm/gitrepo/gogame_bot/python')
from app_global.color_print import CONST

    # '(\ (\'

    # '( -.-)'
    
    # 'o__(")(")'
welcome=[]
welcome.append('                                                           ')
welcome.append('     (\ (\                                                 ')
welcome.append('  *  ( -.-)   * * * * * * * * * * * * * * * * *            ')
welcome.append('  *  O_(")(")                                    *         ')
welcome.append('  *                 Go game AI and Robot            *      ')
welcome.append('  *                     Version 0.38                  *    ')
welcome.append('  *                                                     *  ')
welcome.append('  *     Copyright @2020 Shandong Perfect PTE.LTD.       *  ')
welcome.append('  *           http://voicevon.vicp.io:7005              *  ')
welcome.append('  *                                                     *  ')
welcome.append('  *                                                     *  ')
welcome.append('  *                System is loading...                 *  ')
welcome.append('  *                                                     *  ')
welcome.append('  * * * * * * * * * * * * * * * * * * * * * * * * * * * *  ')
welcome.append('                                                           ')
for w in welcome:
    print('                      ' + CONST.print_color.control.bold + CONST.print_color.fore.yellow + CONST.print_color.background.blue + w + CONST.print_color.control.reset)
print(CONST.print_color.control.reset)

if True:
    from mainSMF import GoManager
    system = GoManager()
    system.start()
    while True:
        system.main_loop()

    # '(\_______/)'
    # ' (= ^.^ =)'
    # '  (")_(")'


