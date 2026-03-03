from app.services.search.tree.huffman_tree import HuffmanTree

#ht = HuffmanTree("dddddddddddddddeeeeeeeeeeeeeeeeeeeeeeeeeeeessssssssssssaaaaaaaaaaiiiiimmmmmmmmmmmmmooooooonnnnnnnnnn")
ht = HuffmanTree("MADURO")
print(ht.search('a'))
ht.plot('huffman.png')
ht.search_plot('o', 'huffman_destacado.png')
