def annotate(ax, yOffsets):
    # Annotate
    ax.axvline(x='2020-09-18', linestyle='dashed', alpha=0.5, color='#6BADEF')
    ax.text(x='2020-09-19', y=yOffsets[0], s='2nd lockdown', alpha=0.7, color='#000000')

    ax.axvline(x='2020-09-01', linestyle='dashed', alpha=0.5, color='#6BADEF')
    ax.text(x='2020-09-02', y=yOffsets[1], s='Schools open', alpha=0.7, color='#000000')