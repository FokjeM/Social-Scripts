import argparse


def floorgold(loc: int, floor: int) -> int:
    base = 140
    add = 2 * loc
    return base + add + floor


def fam_calc(exact_fam: int) -> int:
    if exact_fam > 2999:
        return 10
    reduce = exact_fam % 300
    calc_fam = exact_fam - reduce
    return int(calc_fam / 300)


def basegold(loc: int, floor: int, fam: int, clan: int) -> float:
    flg = floorgold(loc, floor)
    fam_boost = fam_calc(fam)
    boost = 100 + fam_boost + clan
    return flg * (boost / 100)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate the best-earning floor for yourself!"
    )
    parser.add_argument("--location", "--loc", "-l", default=1, type=int,
                        help="The location to calculate the earnings for.")
    parser.add_argument("--floor", "-f", default=1, type=int,
                        help="The floor of the location to calculate for.")
    parser.add_argument("--clan", "-c", default=0, type=int,
                        help="The clan gold bonus, percentage value")
    parser.add_argument("--familiarity", "--fam", default=0, type=int,
                        help="The familiarity of the card you battle with")
    parser.add_argument("--deviance", "-d", default=False,
                        action="store_true",
                        help="Whether or not to print min and max with RNG")
    args = parser.parse_args()
    print(f"Earning for {args.location}-{args.floor}")
    fg = floorgold(args.location, args.floor)
    print(f"Base gold earned on this floor:{fg}")
    bg = int(basegold(args.location, args.floor,
                  clan=args.clan, fam=args.familiarity))
    print(f"Gold earned with clan and familiarity bonuses: {bg}")
    if args.deviance is True:
        print(f"Absolute minimum: {int(bg*0.9)}")
        print(f"Absolute maximum: {int(bg*1.1)}")
    exit(0)
