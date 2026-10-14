# Visualization Fundamentals - Theory

## 1. Chart selection by variable type

- One categorical variable: bar chart of counts or proportions. Bar length
  encodes value against a zero baseline.
- One continuous variable: histogram (binned counts) or dot plot for small n.
- Two continuous variables: scatter plot; add a binned-mean trend if dense.
- Time-ordered values: line chart with uniform time spacing on the x-axis.
- Part-to-whole: stacked bars, not pie slices - angles and areas are judged
  far less accurately than aligned lengths.

## 2. The honest-axis rules

- Quantitative bar and histogram axes start at zero; truncating the y-axis
  turns small differences into dramatic ones.
- Never use dual y-axes with independent scales: rescaling either series
  flips which "leads", so any crossing is arbitrary.
- Keep aspect and binning fixed when comparing panels; changing bins between
  groups manufactures differences.
- Log scales are for multiplicative relationships; label them loudly, since
  equal distances mean multiplication, not addition.

## 3. The Anscombe lesson

F. J. Anscombe's 1973 quartet gives four (x, y) datasets with effectively
identical summary statistics (mean of x = 9, mean of y = 7.5, correlation
about 0.816) but completely different graphs: clean linear cloud, curved
relationship, one-point outlier lever, and a vertical line with one far
point. No table of means detects this; only plotting does. Rule: graph
before you model, every time.

## 4. Overplotting and its mitigations

When thousands of points share pixels, density becomes invisible. Responses:

- Alpha blending: draw points semi-transparent so dark regions read as dense.
- Jitter: add small random offsets to discrete-valued axes to separate ties.
- Binning: aggregate into cells and show counts or cell means (the approach
  computed in this lab's snippets).
- Sampling or contour summaries when the data exceeds the pixel budget.

## 5. Text charts as a discipline

Printing `#` bars forces explicit bin edges, counts, and scales - the same
decisions a graphics library hides. If the text version is ambiguous, the
graphical one will be too.
