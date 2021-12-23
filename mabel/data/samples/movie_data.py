import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], "../../.."))

from mabel.data.internals.relation import Relation


class MovieData(Relation):
    def __init__(self):
        SCHEMA = {
            "YEAR": {"type": "int"},
            "MOVIE": {"type": "str"},
            "GENRE": {"type": "str"},
            "MPAA": {"type": "str"},
            "RATING": {"type": "str"},
            "DISTRIBUTOR": {"type": "str"},
            "TOTAL FOR YEAR": {"type": "int"},
            "TOTAL IN 2019 DOLLARS": {"type": "int"},
            "TICKETS SOLD": {"type": "int"},
        }

        # fmt:off
        DATA = [
            (1995,"Batman Forever","Drama","PG-13","Warner Bros.",184031112,387522978,42306002,),
            (1996,"Independence Day","Adventure","PG-13","20th Century Fox",306169255,634504608,69269062,),
            (1997,"Men in Black","Adventure","PG-13","Sony Pictures",250650052,500207943,54607854,),
            (1998,"Titanic","Adventure","PG-13","Paramount Pictures",443319081,865842808,94524324,),
            (1999,"Star Wars Ep. I: The Phantom Menace","Adventure","PG","20th Century Fox",430443350,776153749,84732942,),
            (2000,"How the Grinch Stole Christmas","Adventure","PG","Universal",253367455,430583644,47006948,),
            (2001,"Harry Potter and the Sorcerer’s Stone","Adventure","PG","Warner Bros.",300404434,486166890,53074988,),
            (2002,"Spider-Man","Adventure","PG-13","Sony Pictures",403706375,636480273,69484746,),
            (2003,"Finding Nemo","Adventure","G","Walt Disney",339714367,516050346,56337374,),
            (2004,"Shrek 2","Adventure","PG","Dreamworks SKG",441226247,650826473,71050925,),
            (2005,"Star Wars Ep. III: Revenge of the Sith","Action","PG-13","20th Century Fox",380270577,543413171,59324582,),
            (2006,"Pirates of the Caribbean: Dead Man’s Chest","Action","PG-13","Walt Disney",423315812,591995851,64628368,),
            (2007,"Spider-Man 3","Adventure","PG-13","Sony Pictures",336530303,448054878,48914288,),
            (2008,"The Dark Knight","Adventure","PG-13","Warner Bros.",531001578,677433772,73955652,),
            (2009,"Transformers: Revenge of the Fallen","Action","PG-13","Paramount Pictures",402111870,491112631,53614916,),
            (2010,"Toy Story 3","Action","G","Walt Disney",415004880,481805411,52598844,),
            (2011,"Harry Potter and the Deathly Hallows: Part II","Action","PG-13","Warner Bros.",381011219,440108798,48046812,),
            (2012,"The Avengers","Adventure","PG-13","Walt Disney",623357910,717331462,78311295,),
            (2013,"Iron Man 3","Adventure","PG-13","Walt Disney",408992272,460808016,50306552,),
            (2014,"Guardians of the Galaxy","Adventure","PG-13","Walt Disney",333055258,373413235,40765637,),
            (2015,"Star Wars Ep. VII: The Force Awakens","Action","PG-13","Walt Disney",742208942,806480887,88043765,),
            (2016,"Finding Dory","Action","PG","Walt Disney",486295561,514967322,56219140,),
            (2017,"Star Wars Ep. VIII: The Last Jedi","Action","PG-13","Walt Disney",517218368,528173936,57660910,),
            (2018,"Black Panther","Action","PG-13","Walt Disney",700059566,703901821,76845177,),
            (2019,"Avengers: Endgame",None,"PG-13","Walt Disney",858373000,858373002,93708843,),
            (2020,"Bad Boys For Life",None,"R","Sony Pictures",204417855,204417848,22316359,),
            (2021,"Shang-Chi and the Legend of the Ten Rings",None,"PG-13","Walt Disney",224226704,224226704,24478897,),
        ]
        # fmt:on

        super().__init__(DATA, header=SCHEMA, name="MovieData")


if __name__ == "__main__":

    md = MovieData()

    print(md.count())
    print(md.apply_selection(lambda r: r[4] == "Walt Disney").count())
    print(md.apply_projection("DISTRIBUTOR").distinct().count())
    print(md.apply_projection("DISTRIBUTOR").distinct().materialize())
    print(md.apply_projection("DISTRIBUTOR").distinct().attributes())
