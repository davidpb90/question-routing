from initialize import init_db
from JointComplexityAlgorithms import calculate_degrees

import pickle

df, dfC,dfV=init_db()
degrees=calculate_degrees(df,10)
pickle.dump(degrees, open( "tree_degrees_travel.p", "wb" ) )
