from analyze import Vector,Analyze


global vector
vector = Vector()
vector.set_corpus(collection_name="poi",key="Categories")
vector.set_initial_vector(collection_name="categories",key="Name")

global analyze
analyze = Analyze()
