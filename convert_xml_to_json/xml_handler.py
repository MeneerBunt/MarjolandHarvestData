import xmltodict
from typing import List
from collections import OrderedDict


class XmlHandler:
    @staticmethod
    def read_xml_file(file_path: str) -> OrderedDict:
        file = open(file_path, mode="rb")
        blob_content = file.read()
        return xmltodict.parse(blob_content)

    @staticmethod
    def parse_harvest_xml_to_json(content_dict: OrderedDict) -> List[dict]:
        # Walk through the XML and append items, saving metadata on the way
        rows = []

        # Root elements
        root_dict = {
            'endtime': content_dict['harvestinfo']['@endtime'],
            'id': content_dict['harvestinfo']['@id'],
            'packageid': content_dict['harvestinfo']['@packageid'],
            'starttime': content_dict['harvestinfo']['@starttime'],
            'type': content_dict['harvestinfo']['@type'],
        }

        # Harvestinfo-metadata metadata
        for sub_dict in content_dict['harvestinfo']['metadata']['field']:
            root_dict[sub_dict['@name']] = sub_dict['@value']

        # Iterate over lots
        for key, value in content_dict['harvestinfo']['lots'].items():
            lot_dict = root_dict

            # Top-level elements
            lot_dict['lot_id'] = value['@id']
            lot_dict['lot_number'] = value['@number']

            # Add lot-level metadata
            for sub_dict in value['metadata']['field']:
                root_dict[sub_dict['@name']] = sub_dict['@value']

            # Iterate over classifications
            for classification in value['classifications']['classification']:
                class_dict = lot_dict
                class_dict['classification_nr'] = classification['@nr']
                class_dict['classification_products_pieces'] = classification['products']['@pieces']
                for sub_dict in classification['metadata']['field']:
                    class_dict[sub_dict['@name']] = sub_dict['@value']

                # Iterate over parameter-groups
                for params_dict in classification['products']['parameter']:
                    params_new_naming = {key[1:]: value for key, value in params_dict.items()}
                    params_new_naming['parameter_id'] = params_new_naming.pop('id')
                    params_new_naming.update(class_dict)
                    rows.append(params_new_naming)
        return rows
