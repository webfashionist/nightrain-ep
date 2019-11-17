__author__ = 'webfashionist'

import plistlib


class Configurations:

    def compile_plist(self, filename):
        plist = self.read(filename)
        plist["CFBundleShortVersionString"] = '0.0.0'
        plist["CFBundleIconFile"] = "icon.icns"
        plist["NSAppTransportSecurity"] = {
            "NSAllowsArbitraryLoads": True,
            "NSExceptionDomains": {
                "localhost": {
                    "NSExceptionAllowsInsecureHTTPLoads": True
                }
            }
        }
        self.write(plist, filename)


    def read(self, filename):
        with open(filename, 'rb') as fp:
            return plistlib.load(fp)

    def get(self, plist):
        print(plist)

    def write(self, plist, filename):
        with open(filename, 'wb') as fp:
            plistlib.dump(plist, fp)
