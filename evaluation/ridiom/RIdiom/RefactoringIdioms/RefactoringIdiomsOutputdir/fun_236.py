def make_tree():
    tree = Node(1)
    tree.left = Node(2)
    tree.right , tree.left.left , tree.left.right  = Node(3), Node(4), Node(5)
    return tree
