def annotate(ax, yOffsets):
    ax.axvline(x='2020-09-18', linestyle='dashed', alpha=0.5, color='#6BADEF')
    ax.text(x='2020-09-19', y=yOffsets[0], s='2nd lockdown', alpha=0.7, color='#000000')

    ax.axvline(x='2020-12-27', linestyle='dashed', alpha=0.5, color='#6BADEF')
    ax.text(x='2020-12-28', y=yOffsets[0], s='3rd lockdown', alpha=0.7, color='#000000')

    ax.axvline(x='2021-01-08', linestyle='dashed', alpha=0.5, color='#6BADEF')
    # ax.text(x='2021-01-09', y=yOffsets[0], s='tighten', alpha=0.7, color='#000000')

    # ax.axvline(x='2020-09-01', linestyle='dashed', alpha=0.5, color='#6BADEF')
    # ax.text(x='2020-09-02', y=yOffsets[1], s='Schools open', alpha=0.7, color='#000000')

def annotateEndLockdown2(ax, yOffsets):
    ax.axvline(x='2020-10-18', linestyle='dashed', alpha=0.5, color='#6BADEF')
    ax.text(x='2020-10-19', y=yOffsets[0], s='End lockdown', alpha=0.7, color='#000000')

def annotateVaccines(ax, yOffsets):
    # Sources:
    # https://he.wikipedia.org/wiki/%D7%9C%D7%AA%D7%AA_%D7%9B%D7%AA%D7%A3#cite_note-15
    ax.axvline(x='2021-01-10', linestyle='dashed', alpha=0.5, color='#685BB1')
    ax.text(x='2021-01-10', y=yOffsets[0]+2, s='Start 2nd dose', alpha=0.7, color='#000000')

    # https: // www.maariv.co.il / corona / corona - israel / Article - 814641
    ax.axvline(x='2021-01-13', linestyle='dashed', alpha=0.5, color='#685BB1')
    ax.text(x='2021-01-13', y=yOffsets[0], s='50+', alpha=0.7, color='#000000')

    # https://www.mako.co.il/news-lifestyle/2021_q1/Article-746b21484c50771027.htm
    ax.axvline(x='2021-01-17', linestyle='dashed', alpha=0.5, color='#685BB1')
    ax.text(x='2021-01-17', y=yOffsets[0]-2, s='45+', alpha=0.7, color='#000000')

    # https://www.mako.co.il/news-lifestyle/2021_q1/Article-3511a989fb91771027.htm
    ax.axvline(x='2021-01-19', linestyle='dashed', alpha=0.5, color='#685BB1')
    ax.text(x='2021-01-19', y=yOffsets[0]-4, s='40+', alpha=0.7, color='#000000')

    # https://www.ynet.co.il/news/article/HJQkIN00Jd
    ax.axvline(x='2021-01-23', linestyle='dashed', alpha=0.5, color='#685BB1')
    ax.text(x='2021-01-23', y=yOffsets[0] + 2, s='16-18', alpha=0.7, color='#000000')

    # https: // news.walla.co.il / item / 3414384
    ax.axvline(x='2021-01-27', linestyle='dashed', alpha=0.5, color='#685BB1')
    ax.text(x='2021-01-27', y=yOffsets[0], s='35+', alpha=0.7, color='#000000')

    # https://www.haaretz.co.il/health/corona/1.9506936
    ax.axvline(x='2021-02-04', linestyle='dashed', alpha=0.5, color='#685BB1')
    ax.text(x='2021-02-04', y=yOffsets[0], s='All ages', alpha=0.7, color='#000000')