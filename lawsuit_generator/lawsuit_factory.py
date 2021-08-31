from datetime import date, datetime
import json

from faker import Faker

from lawsuit_generator.fake_lawsuit import FakeFolder, FakeLawsuit


class LawsuitFactory():
    def __init__(self):
        self.fake = Faker(["pt_BR", "pt-BR"])

    def generate_fake_dv(self, nup_id: str, nup_year: str, nup_seg: str,
                        nup_region: str, nup_orig: str) -> str:
        """Generate a fake lawsuit number verification digit based calculation.

        Calculation: mod97 in base 10

        :param nup_id: Lawsuit id - First 7 digits
        :type nup_id: str
        :param nup_year: Lawsuit year start
        :type nup_year: str
        :param nup_seg: Lawsuit juridical segment
        :type nup_seg: str
        :param nup_region: Lawsuit state/region
        :type nup_region: str
        :param nup_orig: Lawsuit origin
        :type nup_orig: str
        :return: Validation digit calculated
        :rtype: str
        """
        number_no_digit = int(nup_id + nup_year + nup_seg + nup_region + nup_orig)
        dv = 98 - ((number_no_digit * 100 % 97) % 97)
        return str(dv).zfill(2)

    def generate_nup(self) -> dict:
        """Generates a fake lawsuit number following CNJ mask and rule.

        mask = xxxxxxx-xx.xxxx.x.xx.xxxx
        rule = got from method generate_fake_dv

        :return: Dict containing lawsuit number and infos gathered from it
        :rtype: dict
        """
        nup_id = str(self.fake.random_number(digits=7, fix_len=True))
        nup_year = str(self.fake.year())
        nup_seg = str(self.fake.random_choices(elements=("4", "5", "8"), length=1)[0])
        nup_region = str(self.fake.random_int(min=1, max=28, step=1)).zfill(2)
        nup_orig = str(self.fake.random_number(digits=4, fix_len=True))
        nup_dv = self.generate_fake_dv(nup_id, nup_year, nup_seg, nup_region, nup_orig)
        full_nup = f"{nup_id}-{nup_dv}.{nup_year}.{nup_seg}.{nup_region}.{nup_orig}"
        court_house = self.dispatch_court(nup_seg, nup_region)
        return {"complete": full_nup,
                "year": nup_year,
                "segment": nup_seg,
                "region": nup_region,
                "origin": nup_orig,
                "court_house": court_house}

    def generate_part(self, lawyer: bool=False) -> dict:
        """Generate fake lawsuit part with random information

        :param lawyer: If is lawyer or not, defaults to False
        :type lawyer: bool, optional
        :return: Random informations generated
        :rtype: dict
        """
        if lawyer:
            part_type = "person"
        else:
            part_type = self.fake.random_choices(elements=("person", "company", None),
                                            length=1)[0]
        if not part_type:
            return None
        if part_type == "person":
            name = self.fake.name()
            if not lawyer:
                doc = self.fake.random_choices(elements=(self.fake.cpf(),
                                                    "%s%s.%s%s%s.%s%s%s-%s" % tuple(self.fake.rg()),
                                                    None),
                                        length=1)[0]
            else:
                lawyer_state = self.fake.state_abbr()
                lawyer_id = str(self.fake.random_number(digits=6, fix_len=True))
                doc = lawyer_state + lawyer_id
            if doc:
                return {"nome": name, "documento": doc}
            else:
                return {"nome": name}
        elif part_type == "company":
            name = self.fake.company()
            doc = self.fake.random_choices(elements=(self.fake.cnpj(), None), length=1)[0]
            if doc:
                return {"nome": name, "documento": doc}
            else:
                return {"nome": name}
        else:
            return None

    def generate_header(self, nup: str, instancia: int, court_house: str) -> dict:
        """Generate fake randomic lawsuit header datas.

        :param nup: Lawsuit number
        :type nup: str
        :param instancia: Lawsuit instance
        :type instancia: int
        :param court_house: Court house where lawsuit is 'running'
        :type court_house: str
        :return: randomic header dictionary
        :rtype: dict
        """
        with open("./lawsuit_generator/court_state_relation.json", "r") as json_states:
                states_dict = json.load(json_states)
        if "TRT" in court_house:
            state_name = "Trabalhista"
        elif "TRF" in court_house:
            state_name = "Federal"
        else:
            state_abbr = court_house[2:]
            state_name = states_dict["STATES"][state_abbr.upper()]

        headers_dict = dict()
        headers_dict["numero_processo"] = nup
        headers_dict["instancia"] = instancia
        law_class = self.fake.random_choices(elements=("Procedimento Comum",
                                                "Execução Extrajudicial",
                                                "Cumprimento de Senteça"),
                                        length=1)[0]
        headers_dict["classe"] = law_class
        
        subject = self.fake.random_choices(elements=(self.fake.paragraph(nb_sentences=1),
                                                None),
                                    length=1)[0]
        if subject:
            headers_dict["assunto"] = subject
        
        forum = self.fake.random_choices(elements=(f"Foro {state_name}", None),
                                    length=1)[0]
        if forum:
            headers_dict["foro"] = forum
        
        area = self.fake.random_choices(elements=("Cível", None), length=1)[0]
        if area:
            headers_dict["area"] = area
        
        branch = f"{str(self.fake.random_int(min=1, max=9, step=1))}a Vara {state_name}"
        district = f"Comarca {state_name}"
        district_or_branch = self.fake.random_choices(elements=("vara", "comarca", None),
                                        length=1)[0]
        if district_or_branch:
            if district_or_branch == "vara":
                headers_dict["vara"] = branch
            else:
                headers_dict["comarca"] = district
        
        gen_url = self.fake.boolean()
        if gen_url:
            url = self.fake.uri() + self.fake.uri_path() + self.fake.uri_page() + self.fake.uri_extension()
            headers_dict["url_processo"] = url
        
        judge = self.fake.random_choices(elements=(self.fake.name(), None), length=1)[0]
        if judge:
            headers_dict["juiz"] = judge
        
        distribution = self.fake.random_choices(elements=(self.fake.date("%d/%m/%Y"), None),
                                        length=1)[0]
        if distribution:
            headers_dict["distribuicao"] = distribution
        
        value_cause = self.fake.random_choices(elements=("{:.2f}".format(self.fake.random_int(min=1000, max=1000000, step=1)),
                                                    None),
                                        length=1)[0]
        if value_cause:
            headers_dict["valor_causa"] = f"R$ {value_cause.replace('.', ',')}"
        return headers_dict

    def generate_progress(self, min_year: str, total_progress: int=1) -> list:
        """Generates a fake quantity of progress data.

        :param min_year: Minimal year base to generate
        :type min_year: str
        :param total_progress: Total of progress to generate, defaults to 1
        :type total_progress: int, optional
        :return: List of fake progress generated
        :rtype: list
        """
        progress_list = list()
        start_date = datetime.strptime(f"{min_year}-01-01", "%Y-%m-%d")
        for _ in range(0, total_progress):
            progress_dict = dict()
            date = self.fake.date_between(start_date=start_date, end_date="now")
            progress_dict["data_movimentacao"] = date.strftime("%Y-%m-%d")
            progress = self.fake.paragraph(nb_sentences=self.fake.random_int(min=1, max=50))
            progress_dict["movimentacao"] = progress
            if self.fake.boolean():
                url = self.fake.uri() + self.fake.uri_path() + self.fake.uri_page() + "/" + self.fake.uri_extension()
                progress_dict["url_documento"] = url
            progress_list.append(progress_dict)
        return progress_list

    def generate_publication(self, min_year: str, lawsuit_number: str,
                             law_class: str, parts_name: str, lawyers_name: str,
                             total_publications: int=1) -> list:
        """Generates a fake quantity of progress data.

        :param min_year: Minimal year base to generate
        :type min_year: str
        :param lawsuit_number: Number of lawsuit
        :type lawsuit_number: str
        :param law_class: Class of the lawsuit, present in header
        :type law_class: str
        :param parts_name: List of the name of both active and passive parts
        :type parts_name: str
        :param lawyers_name: List of the name of active and passive lawyers
        :type lawyers_name: str
        :param total_publications: Total of progress to generate, defaults to 1
        :type total_publications: int, optional
        :return: List of fake progress generated
        :rtype: list
        """
        publications_list = list()
        start_date = datetime.strptime(f"{min_year}-01-01", "%Y-%m-%d")
        for _ in range(0, total_publications):
            publication_dict = dict()
            date = self.fake.date_between(start_date=start_date, end_date="now")
            publication_dict["data_publicacao"] = date.strftime("%Y-%m-%d")
            
            publication = self.fake.paragraph(nb_sentences=self.fake.random_int(min=1, max=50))
            full_publication_text = f"{law_class.upper()} - PROCESSO {lawsuit_number} - {parts_name} - {publication} - adv: {lawyers_name}"
            publication_dict["publicacao"] = full_publication_text
            if self.fake.boolean():
                url = self.fake.uri() + self.fake.uri_path() + self.fake.uri_page() + "/" + self.fake.uri_extension()
                publication_dict["url_documento"] = url
            publications_list.append(publication_dict)
        return publications_list

    def generate_appendix(self, min_year: str, total_appendix: int=1) -> list:
        """Generates a fake quantity of appendix data.

        :param min_year: Minimal year base to generate
        :type min_year: str
        :param total_progress: Total of appendix to generate, defaults to 1
        :type total_progress: int, optional
        :return: List of fake appendix generated
        :rtype: list
        """
        appendix_list = list()
        start_date = datetime.strptime(f"{min_year}-01-01", "%Y-%m-%d")
        for _ in range(0, total_appendix):
            appendix_dict = dict()
            date = self.fake.date_between(start_date=start_date, end_date="now")
            appendix_dict["data_documento"] = date.strftime("%Y-%m-%d")
            description = self.fake.paragraph(nb_sentences=self.fake.random_int(min=1, max=5))
            appendix_dict["descricao"] = description
            url = self.fake.uri() + self.fake.uri_path() + self.fake.uri_page() + "/" + self.fake.uri_extension()
            appendix_dict["url_documento"] = url
            appendix_list.append(appendix_dict)
        return appendix_list

    def generate_petition(self, min_year: str, total_petition: int=1):
        """Generates a fake quantity of petition data.

        :param min_year: Minimal year base to generate
        :type min_year: str
        :param total_progress: Total of petition to generate, defaults to 1
        :type total_progress: int, optional
        :return: List of fake petitions generated
        :rtype: list
        """
        petition_list = list()
        start_date = datetime.strptime(f"{min_year}-01-01", "%Y-%m-%d")
        for _ in range(0, total_petition):
            petition_dict = dict()
            date = self.fake.date_between(start_date=start_date, end_date="now")
            petition_dict["data_peticao"] = date.strftime("%Y-%m-%d")
            petitio_type = self.fake.paragraph(nb_sentences=self.fake.random_int(min=1, max=1))
            petition_dict["tipo"] = petitio_type
            petition_list.append(petition_dict)
        return petition_list

    def generate_auditions(self, min_year: str, total_auditions: int=1):
        """Generates a fake quantity of audition data.

        :param min_year: Minimal year base to generate
        :type min_year: str
        :param total_auditions: Total of audtions to generate, defaults to 1
        :type total_auditions: int, optional
        :return: List of fake auditions generated
        :rtype: list
        """
        audition_list = list()
        start_date = datetime.strptime(f"{min_year}-01-01", "%Y-%m-%d")
        for _ in range(0, total_auditions):
            audition_dict = dict()
            date = self.fake.date_between(start_date=start_date, end_date="now")
            audition_dict["data_audiencia"] = date.strftime("%Y-%m-%d")
            audition_text = self.fake.paragraph(nb_sentences=self.fake.random_int(min=1, max=1))
            audition_dict["audiencia"] = audition_text
            audition_situation = self.fake.paragraph(nb_sentences=self.fake.random_int(min=1, max=1))
            audition_dict["situacao"] = audition_situation[:20]
            audition_dict["qtd_pessoas"] = self.fake.random_int(min=1, max=10)
            audition_list.append(audition_dict)
        return audition_list

    def generate_classification(self, source: list, event_type):
        classifications_list = list()
        classification_names_list = ["classificacao_um", "classificacao_dois",
                                     "classificacao_cinco", "classificacao_quatro"]
        total_itens = len(source)
        percentage = 20
        max_classifications = round((total_itens*percentage)/100)
        total_classifications = self.fake.random_int(min=0, max=max_classifications)
        for _ in range(0, total_classifications):
            source_obj = self.fake.random_choices(elements=source, length=1)[0]
            classification_name = self.fake.random_choices(elements=classification_names_list,
                                                           length=1)[0]
            #NOTE Subtracted by 10 to have something left as an end
            start_position = total_classifications = self.fake.random_int(min=0, max=len(source_obj["publicacao"])-10)
            end_position = total_classifications = self.fake.random_int(min=start_position, max=len(source_obj["publicacao"]))
            term = source_obj["publicacao"][start_position:end_position]
            classification_obj = {
                "evento_obj": source_obj,
                "tipo_evento": event_type,
                "classificacao": classification_name,
                "ativo": True,
                "match": {
                    "inicio": start_position,
                    "fim": end_position,
                    "termo": term
                }
            }
            classifications_list.append(classification_obj)
        return classifications_list        

    def generate_status(self) -> str:
        """Generate a fake status classification for lawsuit.

        :return: Random classification option
        :rtype: str
        """
        return self.fake.random_choices(elements=("ativo", "arquivado", "suspenso", None),
                                length=1)[0]

    def generate_full_lawsuit(self, lw_instance: int=1, is_main: bool=True,
                              is_appeal: bool=False, is_recourse: bool=False,
                              is_attached: bool=False, is_dependent: bool=False,
                              is_secret: bool=False) -> FakeLawsuit:
        """Generate full fake lawsuit.

        :param lw_instance: Instance reference, defaults to 1
        :type lw_instance: int, optional
        :param is_main: If the lawsuit is a main or not, defaults to True
        :type is_main: bool, optional
        :param is_appeal: If the lawsuit is an appeal, defaults to False
        :type is_appeal: bool, optional
        :param is_recourse: If the lawsuit is a recourse, defaults to False
        :type is_recourse: bool, optional
        :param is_attached: If the lawsuit is attached to the main, defaults to False
        :type is_attached: bool, optional
        :param is_dependent: If the lawsuit is a dependent lawsuit, defaults to False
        :type is_dependent: bool, optional
        :param is_secret: If the lawsuit is in justice secret, defaults to False
        :type is_secret: bool, optional
        :return: Full lawsuit generated
        :rtype: FakeLawsuit
        """
        number_info_dict = self.generate_nup()
        status = self.generate_status()
        if is_secret:
            header = {"secret": "Dados apenas no tribunal"}
            progress_list = list()
            appendix_list = list()
            publication_list = list()
            petition_list = list()
            audition_list = list()
            classification_list = list()
            part_active_list = list()
            part_active_lawyer_list = list()
            part_passive_list = list()
            part_passive_lawyer_list = list()
            part_others_list = list()
        else:
            header = self.generate_header(nup=number_info_dict["complete"],
                                          instancia=lw_instance,
                                          court_house=number_info_dict["court_house"])
            
            part_active_list = [self.generate_part() for x in range(0, self.fake.random_int(min=0, max=5))]
            part_active_lawyer_list = [self.generate_part(lawyer=True) for x in range(0, self.fake.random_int(min=0, max=5))]
            part_passive_list = [self.generate_part() for x in range(0, self.fake.random_int(min=0, max=5))]
            part_passive_lawyer_list = [self.generate_part(lawyer=True) for x in range(0, self.fake.random_int(min=0, max=5))]
            part_others_list = [self.generate_part() for x in range(0, self.fake.random_int(min=0, max=5))]
            
            parts_name = list()
            if part_active_list:
                parts_name += [x["nome"] for x in part_active_list if x]
            if part_passive_list:
                parts_name += [x["nome"] for x in part_passive_list if x]
            lawyers_name = list()
            if part_active_lawyer_list:
                lawyers_name += [x["nome"] for x in part_active_lawyer_list if x]
            if part_passive_lawyer_list:
                lawyers_name += [x["nome"] for x in part_passive_lawyer_list if x]
            publication_list = self.generate_publication(min_year=number_info_dict["year"],
                                                         lawsuit_number=number_info_dict["complete"],
                                                         law_class=header.get("classe", ""),
                                                         parts_name=" - ".join(parts_name),
                                                         lawyers_name=" - ".join(lawyers_name),
                                                         total_publications=self.fake.random_int(min=0, max=100))
            progress_list = self.generate_progress(min_year=number_info_dict["year"],
                                                   total_progress=self.fake.random_int(min=0, max=100))
            appendix_list = self.generate_appendix(min_year=number_info_dict["year"],
                                                   total_appendix=self.fake.random_int(min=0, max=50))
            petition_list = self.generate_petition(min_year=number_info_dict["year"],
                                                   total_petition=self.fake.random_int(min=0, max=30))
            audition_list = self.generate_auditions(min_year=number_info_dict["year"],
                                                    total_auditions=self.fake.random_int(min=0, max=30))
            classification_list = self.generate_classification(publication_list, "publicacao")
        fake_obj = FakeLawsuit(lawsuit_number=number_info_dict["complete"],
                               year=number_info_dict["year"],
                               segment=number_info_dict["segment"],
                               region=number_info_dict["region"],
                               origin=number_info_dict["origin"],
                               court_house=number_info_dict["court_house"],
                               status=status,
                               instance=lw_instance,
                               is_main=is_main,
                               is_appeal=is_appeal,
                               is_recourse=is_recourse,
                               is_attached=is_attached,
                               is_dependent=is_dependent,
                               is_secret=is_secret,
                               header=header,
                               petition=petition_list,
                               audition=audition_list,
                               progress=progress_list,
                               appendix=appendix_list,
                               publication=publication_list,
                               classification=classification_list,
                               part_active=part_active_list,
                               part_active_lawyer=part_active_lawyer_list,
                               part_passive=part_passive_list,
                               part_passive_lawyer=part_passive_lawyer_list,
                               part_others=part_others_list,)
        return fake_obj

    def generate_full_folder(self) -> FakeFolder:
        """Generate complete folder, with multiple lawsuits related.

        :return: Folder folder generated
        :rtype: FakeFolder
        """
        is_secret = self.fake.boolean(chance_of_getting_true=20)
        main_lawsuit = self.generate_full_lawsuit(lw_instance=1, is_main=True, is_secret=is_secret)
        if is_secret:
            main_number = main_lawsuit.lawsuit_number
            book_name = f"{main_number}: SEGREDO DE JUSTIÇA"
            court_house = main_lawsuit.court_house
            appeals = list()
            recourses = list()
            attached = list()
            dependents = list()
        else:
            main_number = main_lawsuit.lawsuit_number
            book_name = f"{main_number}: PROCESSO GERADO"
            court_house = main_lawsuit.court_house
            appeals = [self.generate_full_lawsuit(lw_instance=1, is_main=False,
                                             is_appeal=True) for x in range(0, self.fake.random_int(min=0, max=3))]
            attached = [self.generate_full_lawsuit(lw_instance=1, is_main=False,
                                             is_attached=True) for x in range(0, self.fake.random_int(min=0, max=3))]
            dependents = [self.generate_full_lawsuit(lw_instance=1, is_main=False,
                                             is_dependent=True) for x in range(0, self.fake.random_int(min=0, max=3))]
            recourses = [self.generate_full_lawsuit(lw_instance=2, is_main=False,
                                             is_recourse=True) for x in range(0, self.fake.random_int(min=0, max=3))]
        fake_obj = FakeFolder(main_number=main_number,
                              book_name=book_name,
                              court_house=court_house,
                              main=main_lawsuit,
                              appeals=appeals,
                              recourses=recourses,
                              attached=attached,
                              dependent=dependents)
        return fake_obj

    def generate_multiple_folders(self, total_folders: int=2) -> list:
        """Generate multiple lawsuit Folders.

        :param total_folders: Total of Lawsuit Folders to generate, defaults to 2
        :type total_folders: int, optional
        :return: All Folders generated
        :rtype: list
        """
        for _ in range(0, total_folders):
            folder_obj = self.generate_full_folder()
            yield folder_obj

    def dispatch_court(self, segment: str, state: str) -> str:
        """Identifica a forma escrita do tribunal baseado no segmento e no estado.
        Segmentos:
            * 8 = Tribunal Judicial
            * 4 = Tribunal Regional Federal
            * 5 = Tribunal Regional do Trabalho
        Ex.: Segmento: 8, Estado: 26 --> TJSP
        :param segment: Segmento em que o processo esta
        :type segment: str
        :param state: Estado em que o processo esta rolando
        :type state: str
        :return: Sigla do tribunal
        :rtype: str
        """
        if segment == "8" and state == "01":
            return "TJAC"
        elif segment == "8" and state == "02":
            return "TJAL"
        elif segment == "8" and state == "03":
            return "TJAP"
        elif segment == "8" and state == "04":
            return "TJAM"
        elif segment == "8" and state == "05":
            return "TJBA"
        elif segment == "8" and state == "06":
            return "TJCE"
        elif segment == "8" and state == "07":
            return "TJDF"
        elif segment == "8" and state == "08":
            return "TJES"
        elif segment == "8" and state == "09":
            return "TJGO"
        elif segment == "8" and state == "10":
            return "TJMA"
        elif segment == "8" and state == "11":
            return "TJMT"
        elif segment == "8" and state == "12":
            return "TJMS"
        elif segment == "8" and state == "13":
            return "TJMG"
        elif segment == "8" and state == "14":
            return "TJPA"
        elif segment == "8" and state == "15":
            return "TJPB"
        elif segment == "8" and state == "16":
            return "TJPR"
        elif segment == "8" and state == "17":
            return "TJPE"
        elif segment == "8" and state == "18":
            return "TJPI"
        elif segment == "8" and state == "19":
            return "TJRJ"
        elif segment == "8" and state == "20":
            return "TJRN"
        elif segment == "8" and state == "21":
            return "TJRS"
        elif segment == "8" and state == "22":
            return "TJRO"
        elif segment == "8" and state == "23":
            return "TJRR"
        elif segment == "8" and state == "24":
            return "TJSC"
        elif segment == "8" and state == "25":
            return "TJSE"
        elif segment == "8" and state == "26":
            return "TJSP"
        elif segment == "8" and state == "27":
            return "TJTO"
        elif segment == "4":
            return f"TRF{state}"
        elif segment == "5":
            return f"TRT{state}"
        else: # For a default result to test
            return "TJSP"