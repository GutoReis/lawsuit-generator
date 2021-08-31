class FakeLawsuit():
    def __init__(self, **kwargs):
        self.lawsuit_number = kwargs["lawsuit_number"]
        self.year = kwargs["year"]
        self.segment = kwargs["segment"]
        self.region = kwargs["region"]
        self.origin = kwargs["origin"]

        self.court_house = kwargs["court_house"]
        self.status = kwargs.get("status", None)
        self.instance = kwargs.get("instance", None)
        self.is_secret = kwargs.get("is_secret", None)
        self.header = kwargs.get("header", None)

        self.is_main = kwargs.get("is_main", True)
        self.is_appeal = kwargs.get("is_appeal", False)
        self.is_recourse = kwargs.get("is_recourse", False)
        self.is_attached = kwargs.get("is_attaced", False)
        self.is_dependent = kwargs.get("is_dependent", False)

        self.petition_list = kwargs.get("petition", [])
        self.audition_list = kwargs.get("audition", [])
        self.progress_list = kwargs.get("progress", [])
        self.appendix_list = kwargs.get("appendix", [])
        self.publication_list = kwargs.get("publications", [])
        self.classification_list = kwargs.get("classifications", [])

        self.part_active_list = kwargs.get("part_active", [])
        self.part_active_lawyer_list = kwargs.get("part_active_lawyer", [])
        self.part_passive_list = kwargs.get("part_passive", [])
        self.part_passive_lawyer_list = kwargs.get("part_passive_lawyer", [])
        self.part_other_list = kwargs.get("part_other", [])


    def to_json(self):
        json_obj = {
            "lawsuit_number": self.lawsuit_number,
            "year": self.year,
            "segment": self.segment,
            "region": self.region,
            "origin": self.origin,
            "court_house": self.court_house,
            "status": self.status,
            "instance": self.instance,
            "is_secret": self.is_secret,
            "header": self.header,
            "is_main": self.is_main,
            "is_appeal": self.is_appeal,
            "is_recourse": self.is_recourse,
            "petition_list": self.petition_list,
            "audition_list": self.audition_list,
            "progress_list": self.progress_list,
            "appendix_list": self.appendix_list,
            "publication_list": self.publication_list,
            "part_active_list": self.part_active_list,
            "part_active_lawyer_list": self.part_active_lawyer_list,
            "part_passive_list": self.part_passive_list,
            "part_passive_lawyer_list": self.part_passive_lawyer_list,
            "part_other_list": self.part_other_list,
            "classification_list": self.classification_list,
        }
        return json_obj


class FakeFolder():
    def __init__(self, **kwargs):
        self.main_number = kwargs["main_number"]
        self.book_name = kwargs["book_name"]
        self.court_house = kwargs["court_house"]
        self.main_lawsuit = kwargs["main"]
        self.appeals_list = kwargs.get("appeals", [])
        self.recourses_list = kwargs.get("recourses", [])
        self.attached_list = kwargs.get("attached", [])
        self.dependent_list = kwargs.get("dependent", [])

    def to_json(self):
        json_obj = {
            "main_number": self.main_number,
            "book_name": self.book_name,
            "court_house": self.court_house
        }

        json_obj["main"] = self.main_lawsuit.to_json()
        json_obj["appeals"] = [x.to_json() for x in self.appeals_list]
        json_obj["recourses"] = [x.to_json() for x in self.recourses_list]
        json_obj["attached"] = [x.to_json() for x in self.attached_list]
        json_obj["dependents"] = [x.to_json() for x in self.dependent_list]

        return json_obj

        