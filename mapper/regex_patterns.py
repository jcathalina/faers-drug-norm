import re

rm_tablets = re.compile("(.*)(\W|^)\(TABLETS?\)|TABLETS?(\W|$)", re.I)
rm_capsules = re.compile("(.*)(\W|^)\(CAPSULES?\)|CAPSULES?(\W|$)", re.I)
rm_abbr_units = re.compile("\(*(\d*\.*\d*\ *MG\,*\ *\/*\\*\ *\d*\.*\d*\ *(M2|ML)*\ *\,*\+*\ *)\)*",
                           re.I)  # Banda et al. uses sticky matching (y flag) here.
rm_units = re.compile("\(*(\d*\.*\d*\ *MILLIGRAMS?\,*\ *\/*\\*\ *\d*\.*\d*\ *(M2|MILLILITERS?)*\ *\,*\+*\ *)\)*",
                      re.I)  # Banda et al. uses sticky matching (y flag) here.
rm_hcl = re.compile("(HCL|HYDROCHLORIDE)", re.I)
