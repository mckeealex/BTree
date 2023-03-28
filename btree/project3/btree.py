from __future__ import annotations
import collections
import json
from typing import List

# Node Class.
# You may make minor modifications.
class Node():
    def  __init__(self,
                  keys     : List[int]  = None,
                  children : List[Node] = None,
                  parent   : Node = None,
                  isleaf   : bool = False):
        self.keys     = keys
        self.children = children
        self.parent   = parent
        self.isleaf   = isleaf

# DO NOT MODIFY THIS CLASS DEFINITION.
class Btree():
    def  __init__(self,
                  m    : int  = None,
                  root : Node = None):
        self.m    = m
        self.root = None
    # DO NOT MODIFY THIS CLASS METHOD.
    def dump(self) -> str:
        print_tree(self.root)
        # def _to_dict(node) -> dict:
        #     return {
        #         "k": node.keys,
        #         "c": [(_to_dict(child) if child is not None else None) for child in node.children]
        #     }
        # if self.root == None:
        #     dict_repr = {}
        # else:
        #     dict_repr = _to_dict(self.root)
        # return json.dumps(dict_repr,indent=2)
        return ""

    # Insert.
    def insert(self, key: int):
        def rotate(root: Node, pred: int, key):
            
            # CHECK TO DO A ROTAION
            if root.parent:
                l_sib = root.parent.children[pred-1:pred] or None
                r_sib = root.parent.children[pred+1:pred+2] or None

                # DO LEFT SHIFT
                if l_sib and len(l_sib[0].children) != self.m:
                    rotate_left(root, l_sib[0], pred)
                    return True

                # DO RIGHT SHIFT
                elif r_sib and len(r_sib[0].children) != self.m:
                    rotate_right(root, r_sib[0], pred)
                    return True
            
            return False

        def split(root: Node):
            
            # GET THE MEDIAN VALUE OF THE ARRAY
            mid = len(root.keys) // 2 - 1 if len(root.keys) % 2 == 0 else len(root.keys) // 2
            median = root.keys[mid]


            # SPLIT THE ROOT
            left = Node(root.keys[:mid], root.children[:mid + 1], root.parent, root.isleaf)
            right = Node(root.keys[mid+1:], root.children[mid + 1:], root.parent, root.isleaf)

            # RESET PARENTS
            if not root.isleaf:
                for child in left.children:
                    child.parent = left
                for child in right.children:
                    child.parent = right
            
            if root.parent:
                # INSERT KEY INTO PARENT
                index = add_to_keys(root.parent, median)
                root.parent.children.pop()

                # SET THE LEFT AND RIGHT POINTERS OF INSERTED KEY
                root.parent.children[index] = left
                root.parent.children.insert(index + 1, right)
            else:
                # CREATE A NEW ROOT WITH THE MEDIAN
                self.root = Node([median], [left, right], None, False)
                left.parent = self.root
                right.parent = self.root
        
        def helper(root: Node, key: int, pred: int):

            # EMPTY TREE
            if not root:
                self.root = Node([key], [None, None], None, True)
            
            # LEAF NODE
            elif root.isleaf:
                
                # INSERT KEY INTO LEAF
                add_to_keys(root, key)

                # CHECK IF NODE IS OVERFULL
                if len(root.keys) > self.m - 1:
                    # SPLIT/ROTATE
                    split(root)

            else: # ROOT IS NOT LEAF
                i = 0
                while i < len(root.keys) and key > root.keys[i]:
                    i += 1
                
                helper(root.children[i], key, i)

                if len(root.children) > self.m:
                    split(root)

        helper(self.root, key, -1)

    # Delete.
    def delete(self, key: int):

        def rotate_or_merge(root: Node, pred: int):
            # Minimum keys allowed per node
            minkeys = (self.m // 2) - 1 if self.m % 2 == 0 else (self.m // 2)

            # RETRIEVE LEFT AND RIGHT SIBLINGS
            l_sib = root.parent.children[pred-1:pred] or None
            r_sib = root.parent.children[pred+1:pred+2] or None

            

            
            if l_sib and len(l_sib[0].keys) == minkeys: # MERGE LEFT
                # GET KEY IN MIDDLE OF MERGE
                middle = root.parent.keys[pred-1]
                # MAKE MERGED KEY ARRAY
                l_sib[0].keys = l_sib[0].keys + [middle] + root.keys
                # ADD ROOT CHILDREN TO LEFT CHILDREN
                l_sib[0].children.extend(root.children)
                # RESET PARENTS
                if not root.isleaf:
                    for child in l_sib[0].children:
                        child.parent = l_sib[0]
                # REMOVE MIDDLE FROM PARENT
                root.parent.keys.remove(middle)
                # REMOVE ROOT FROM PARENT CHILDREN
                root.parent.children.pop(pred)
            elif r_sib and len(r_sib[0].keys) == minkeys: # MERGE RIGHT
                # GET KEY IN MIDDLE OF MERGE
                middle = root.parent.keys[pred]
                # MAKE MERGED KEY ARRAY
                r_sib[0].keys = root.keys + [middle] + r_sib[0].keys
                # ADD ROOT CHILDREN TO LEFT CHILDREN
                r_sib[0].children = root.children + r_sib[0].children
                # RESET PARENTS
                if not root.isleaf:
                    if not l_sib[0].children:
                        print(l_sib[0].keys)
                    for child in l_sib[0].children:
                        child.parent = l_sib[0]
                # REMOVE MIDDLE FROM PARENT
                root.parent.keys.remove(middle)
                # REMOVE ROOT FROM PARENT CHILDREN
                root.parent.children.pop(pred)
            # OTHERWISE MERGE
            else:
                # TRY TO RIGHT AND LEFT ROTATE
                if l_sib and len(l_sib[0].keys) > minkeys:
                    rotate_right(l_sib[0], root, pred-1)
                elif r_sib and len(r_sib[0].keys) > minkeys:
                    rotate_left(r_sib[0], root, pred + 1)
                
        
        def helper(root: Node, key: int, pred: int):
            # Minimum keys allowed per node
            minkeys = (self.m // 2) - 1 if self.m % 2 == 0 else (self.m // 2)

            # SEARCH FOR KEY IN NODE, OR CHILD INDEX
            index = 0
            while index < len(root.keys) and key > root.keys[index]:
                index += 1

            # CHECK IF WE FOUND THE KEY
            if index < len(root.keys) and root.keys[index] == key:
                # ROOT IS A LEAF
                if root.isleaf:

                    # REMOVE KEY AND CHILD
                    root.keys.remove(key)
                    root.children.pop()

                    # CASE 1: ROOT HAS ENOUGH KEYS TO DELETE/IS THE ROOT
                    if root == self.root:
                        if len(root.keys) == 0:
                            self.root = None
                    # CASE 2: MUST ROTATE/MERGE
                    elif len(root.keys) < minkeys:
                        rotate_or_merge(root, pred)
                                
                else: # ROOT IS NOT A LEAF

                    # GET INORDER SUCCESSOR
                    right, p = root.children[index + 1], index + 1
                    while right.children[0]:
                        p = 0
                        right = right.children[0]
                    
                    # REPLACE KEY WITH SUCCESSOR
                    root.keys[index] = right.keys[0]

                    # DELETE THE SUCCESSOR
                    helper(right, right.keys[0], p)

                    # VERIFY ROOT IS STILL VALID
                    if len(root.keys) < minkeys and root != self.root:
                        rotate_or_merge(root, pred)
                    elif len(root.keys) == 0 and root == self.root:
                        self.root = root.children[0]
                        self.root.parent = None

            else:
                # RECURSE DOWN THE TREE
                helper(root.children[index], key, index)

                # CHECK THAT NODE IS NOT UNDERFULL 
                if len(root.keys) < minkeys:
                    # KEY IS ROOT
                    if root == self.root:
                        if len(root.keys) == 0:
                            self.root = root.children[0]
                            self.root.parent = None

                    # KEY IS INTERNAL
                    else:
                        rotate_or_merge(root, pred)
                        
                    
        # DELETE KEY
        helper(self.root, key, -1)


    # Search
    def search(self,key) -> List[int]:
        # self.dump()
        def helper(root: Node, key: int, path: list[int]):
            index = 0
            while index < len(root.keys) and key > root.keys[index]:
                index += 1
            
            if index < len(root.keys) and root.keys[index] == key:
                return path
            else:
                path.append(index)
                return helper(root.children[index], key, path)
            
        return helper(self.root, key, [])

# ROTATES A KEY LEFT FROM ROOT TO LEFT SIBLING
def rotate_left(root: Node, l_sib: Node, pred: int):
    add_to_keys(l_sib, root.parent.keys[pred - 1], False)
    root.parent.keys[pred - 1] = root.keys.pop(0)
    l_sib.children.append(root.children.pop(0))
    if not l_sib.isleaf:
        l_sib.children[-1].parent = l_sib

# ROTATE A KEY FROM ROOT TO RIGHT SIBLING
def rotate_right(root: Node, r_sib: Node, pred: int):
    add_to_keys(r_sib, root.parent.keys[pred], False)
    root.parent.keys[pred] = root.keys.pop()
    r_sib.children = [root.children.pop()] + r_sib.children[0:]
    if not r_sib.isleaf:
        r_sib.children[0].parent = r_sib

# RETURNS INDEX WHERE KEY IS INSERTED
def add_to_keys(root: Node, key: int, pushChild = True) -> int:
    index = 0
    while index < len(root.keys) and key > root.keys[index]:
        index += 1

    # Add key to keys and expand children array
    root.keys = root.keys[:index] + [key] + root.keys[index:]

    if pushChild:
        root.children.append(None)

    return index

def print_tree(root: Node):
    
    queue = collections.deque([root])
    
    
    while queue:
        print()

        for i in range(len(queue)):
            curr = queue.popleft()
            if curr:
                print(curr.keys, end = "")
                queue.extend(curr.children)