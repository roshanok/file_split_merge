import cProfile
from file_split_merge import SplitAndCombineFiles

cProfile.run(r'SplitAndCombineFiles().split(r"C:\Roshan\ZIP\New folder\f1.zip", "5")', 'split.profile')

cProfile.run(r'SplitAndCombineFiles().merge(r"C:\Roshan\ZIP\New folder\f1.zip")', 'merge.profile')

# python -m pstats tesse_body\app.profile
# radon cc . -e "AI_ENV*" -a -s -o score
# radon raw . -e "AI_ENV*" -a -s -o score
# radon mi . -e "AI_ENV*" -s
# radon hal . -e "AI_ENV*"

