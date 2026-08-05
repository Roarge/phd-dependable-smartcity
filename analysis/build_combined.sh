#!/bin/bash
set -e
cd "$(dirname "$0")"

# Build chapter5_combined.md
> chapter5/chapter5_combined.md
for f in chapter5/chapter5_introduction.md chapter5/section5_{1,2,3,4,5,6,7,8}.md; do
  cat "$f" >> chapter5/chapter5_combined.md
  printf '\n\n' >> chapter5/chapter5_combined.md
done

# Build appendix_combined.md
printf '# Appendix A: Formal Proofs and Computational Results\n\n' > appendix/appendix_combined.md
for f in appendix/appendix_a{0,1,2,3,4,5,6,7}.md; do
  cat "$f" >> appendix/appendix_combined.md
  printf '\n\n' >> appendix/appendix_combined.md
done

# Build final combined
> chapters5_6_appendix_combined.md
cat chapter5/chapter5_combined.md >> chapters5_6_appendix_combined.md
printf '\n\n' >> chapters5_6_appendix_combined.md
cat chapter6/chapter6.md >> chapters5_6_appendix_combined.md
printf '\n\n' >> chapters5_6_appendix_combined.md
cat appendix/appendix_combined.md >> chapters5_6_appendix_combined.md

echo "Done. Lines: $(wc -l < chapters5_6_appendix_combined.md)"
