import attr


@attr.s
class Country:
    iso = attr.ib()
    name = attr.ib()


@attr.s
class City:
    country_iso = attr.ib()
    geoname_id = attr.ib()
    name = attr.ib()
    latitude = attr.ib()
    longitude = attr.ib()
    population = attr.ib()

    @property
    def geonameID(self):
        return self.geoname_id
