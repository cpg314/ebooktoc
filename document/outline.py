from tempfile import NamedTemporaryFile
import subprocess
import re

class Outline(object):
    def __init__(self):
        self._nodes = []
        self._uid = 0

    def create_node(self, name, page, parent=None):
        """
        New node with given name, page and parent
        """
        self._nodes.append({"name": name, "page": page, "parent": parent})
        return len(self._nodes) - 1

    def size(self):
        """
        Outline size (total number of nodes)
        """
        return len(self._nodes)

    def children(self, parent):
        """
        Children of node `parent`
        """
        for i, n in enumerate(self._nodes):
            if n["parent"] == parent:
                yield i

    def get(self, i):
        """
        Return a node from an id
        """
        return self._nodes[i]

    def child(self, parent, i):
        children = list(self.children(parent))
        if len(children) == 0:
            return None
        return children[i]

    def lastchild(self, parent):
        """
        Identifier of last child of node `parent`
        """
        return self.child(parent, -1)

    def firstchild(self, parent):
        """
        Identifier of first child of node `parent`
        """
        return self.child(parent, 0)

    def siblings(self, node):
        """
        Nodes at the same level
        """
        return list(self.children(self._nodes[node]["parent"]))

    def sibling(self, node, i):
        """
        Node at the same level with given index
        """
        siblings = self.siblings(node)
        i = siblings.index(node) + i
        if i < 0 or i >= len(siblings):
            return None
        return siblings[i]

    def previous(self, node):
        """
        Identifier of predecessor of node `node`
        """
        return self.sibling(node, -1)

    def next(self, node):
        """
        Identifier of successor of node `node`
        """
        return self.sibling(node, +1)

    def parent(self, node):
        """
        Identifier of parent of node `node`
        """
        return self._nodes[node]["parent"]

    def sort(self):
        nodes = sorted(self._nodes, key=lambda x: x["page"])
        for i, n in enumerate(nodes):
            p = n["parent"]
            if p is not None:
                nodes[i]["parent"] = nodes.index(self._nodes[p])
        self._nodes = nodes

    def nodes(self):
        """
        Get nodes
        """
        return self._nodes

    def nodeString(self, n, pages):
        nn = self._nodes[n]
        nn["id"] = n
        return ("{name}" +  ("(p. {page} / {id})" if pages else "") + "\n").format(**nn)

    def fromString(self, s):
        level = 0
        parents = [None]
        for ss in s.split("\n"):
            r = re.match("(\d+) (\d+) (.*)", ss)
            if r is not None:
                level2 = int(r.group(1))
                page = int(r.group(2))
                title = r.group(3)
                if level2 > level:
                    parents.append(len(self._nodes) - 1)                    
                elif level2 < level:
                    for i in range(0, level - level2 - 1):
                        parents.pop()
                self.create_node(title, page, parents[-1])
                level = level2
    
    def fromHeaders(self, headers):
        parent = None
        for h in headers:
            words = ["chapter", "index", "contents", "bibliography", "introduction", "acknowledgement"]
            if any([w in h[1].lower() for w in words]):
                parent = self.create_node(h[1], h[0], None)
            else:
                self.create_node(h[1], h[0], parent)

    def __repr__(self):
        return self.show()
    
    def show(self, parent=None, level=0, pages=True):
        """
        Recursively show the tree from node `parent`, up to level `level`
        """
        s = ""
        for n in self.children(parent):
            s = s + level * 4 * " " + self.nodeString(n, pages)
            s = s + self.show(n, level + 1, pages)
        return s

    def editLines(self, lines, parent=None):
        for n in self.children(parent):
            l = lines.pop(0).strip()
            self._nodes[n]["name"] = l
            self.editLines(lines, n)
            
    def edit(self):
        f = NamedTemporaryFile(delete=False)
        out = "# Comment\n" + self.show(pages=False)
        f.write(out.encode("utf-8"))
        f.close()
        subprocess.call(["nano", f.name])
        with open(f.name, "r", encoding="utf-8") as ff:
            lines = [l for l in ff.readlines() if l.strip()[0] != "#"]
            if len(lines) != len(self._nodes):
                exit("Number of lines does not match")
            self.editLines(lines)
        
