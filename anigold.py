import argparse
def floorgold(loc, floor):
    base = 140
    add = 2*int(loc)
    return int(base+add+int(floor))

def fam_calc(exact_fam):
    boost = int(exact_fam)/300
    mult = 100+boost
    return int(mult) if mult < 110 else 110 # Chops off decimals like Math.floor()

def basegold(loc, floor, fam, clan):
    flg = floorgold(loc, floor)
    boost = fam_calc(fam)+int(clan)
    return flg*(int(boost)/100)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process AniGame dex entries")
    parser.add_argument("--location", "--loc", "-l", default=1,
                        help="The location to calculate the earnings for.")
    parser.add_argument("--floor", "-f", default=1,
                        help="The floor of the location to calculate for.")
    parser.add_argument("--clan", "-c", default=0,
                        help="The clan gold bonus, % value")
    parser.add_argument("--familiarity", "--fam", default=0,
                        help="The familiarity of the card you're battling with")
    parser.add_argument("--deviance", "-d", default=False, type=bool,
                        help="Whether or not to print min and max possibilities")
    args = parser.parse_args()
    print(f"Earning for {args.location}-{args.floor}")
    fg = floorgold(args.location, args.floor)
    print(f"Base gold earned on this floor:{fg}")
    bg = basegold(args.location, args.floor, args.clan, args.familiarity)
    print(f"Gold earned with clan and familiarity bonuses: {bg}")
    if args.deviance and str(args.deviance).lower()[0] not in ["f", "n"]:
        print(f"Absolute minimum: {int(bg*0.9)}")
        print(f"Absolute maximum: {int(bg*1.1)}")
    exit(0)
