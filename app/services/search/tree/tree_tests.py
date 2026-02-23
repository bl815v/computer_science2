from app.services.search.tree.digital_tree import DigitalTree
from app.services.search.tree.multiple_residue_tree import MultipleResidueTree
from app.services.search.tree.simple_residue_tree import SimpleResidueTree

dt = DigitalTree(encoding='ABC')
dt.create()
dt.insert('P')
dt.insert('R')
dt.insert('U')
dt.delete('P')
print(dt.search('P'))
dt.plot('digital.png')
dt.search_plot('R', 'destacado.png')

# Simple
st = SimpleResidueTree(encoding='ABC')
st.create()
st.insert('P')
st.insert('R')
st.insert('U')
st.insert('E')
st.plot('simple.png')

# Múltiple
mt = MultipleResidueTree(m=2, encoding='ABC')
mt.create()
mt.insert('P')
mt.insert('R')
mt.insert('U')
mt.insert('E')
mt.plot('multiple.png')
