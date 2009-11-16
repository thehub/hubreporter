class ITree(dict):
    def register(self, o):
        no_ancestors = len(o.__mro__)
        if no_ancestors < 4: return
        oparents = o.__mro__[1:-3][::-1]
        level = self
        for p in oparents:
            if not p in level:
                level[p] = dict()
                level[p][o] = dict()
                return
            level = level[p]
        level[o] = dict()

def printtree(node, i=0):
    keys = node.keys()
    if not keys: return
    print "\t" * i, keys
    i += 1
    for subnode in node.values():
        printtree(subnode, i)

itree = ITree()

class ItemMeta(type):
    def __new__(cls, name, bases, d):
        cls = super(ItemMeta, cls).__new__(cls, name, bases, d)
        cls.name = d.get("name", name)
        itree.register(cls)
        return cls

class Item(object):
    itype = ""
    check_words = []
    __metaclass__ = ItemMeta
    @classmethod
    def check(self, useragent):
        if self.check_words == None:
            return self.name
        for word in self.check_words:
            if word in useragent:
                return self.name
    @classmethod
    def version(self, useragent):
        try:
            return self._version(useragent)
        except:
            return "" 
    @classmethod
    def _version(self, useragent):
        raise NotImplemented

class Browser(Item):
    check_words = None
    itype = "Browser"
    @classmethod
    def _version(self, useragent):
        return useragent.split(self.name + "/")[-1].split()[0]

class OS(Item):
    check_words = None
    itype = "OS"

class Firefox(Browser):
    check_words = ["Firefox"]

class Konqueror(Browser):
    check_words = ["Konqueror"]
    @classmethod
    def _version(self, useragent):
        return useragent.split("Konqueror/")[-1].split()[0]

class Opera(Browser):
    check_words = ["Opera"]
    @classmethod
    def _version(self, useragent):
        return useragent.split("Opera/")[-1].split()[0]

class MSIE(Browser):
    check_words = ["MSIE"]
    name = "Microsoft Internet Explorer"
    @classmethod
    def _version(self, useragent):
        return useragent.split('MSIE')[-1].split(';')[0].strip()

class Linux(OS):
    check_words = ['Linux']

class Macintosh(OS):
    check_words = ['Macintosh']

class MacOS(Macintosh):
    @classmethod
    def _version(self, useragent):
        return useragent.split('Mac OS')[-1].split(';')[0].strip()

class Windows(OS):
    check_words = ['Windows']
    @classmethod
    def _version(self, useragent):
        return useragent.split('Windows')[-1].split(';')[0].strip()

class Ubuntu(Linux):
    check_words = ['Ubuntu']
    @classmethod
    def _version(self, useragent):
        return useragent.split('Ubuntu/')[1].split()[0]

def detect(tree, useragent, result):
    for node in tree:
        if node.check(useragent):
            if node.itype in result:
                result[node.itype].append((node.name, node.version(useragent)))
            else:
                result[node.itype] = [(node.name, node.version(useragent))]
            detect(tree[node], useragent, result)
    return result

def simpledetect(agent):
    ret = dict()
    result = detect(itree, agent, {})
    if "Browser" in result:
        ret["browser"] = " ".join(result['Browser'][-1])
    if "OS" in result:
        os = " ".join(result['OS'][-1])
        ret["os"] = " ".join(result['OS'][-1]),
    return ret


def test():
    import datetime
    then = datetime.datetime.now()
    execfile("access.log", globals())
    for agent in agents:
        print agent
        print simpledetect(agent)
        print 
    now = datetime.datetime.now()
    print len(agents), "analysed in ", now - then


if __name__ == '__main__':
    print
    print itree
    printtree(itree)
    print
    test()
