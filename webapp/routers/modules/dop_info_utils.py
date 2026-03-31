import json
from .common_utils import product_name, name_photo, MR_country
import aiofiles


async def DopInfo_photo(id_row_user: list[str], lang: str, ConditionsData: dict):
    dop_info = ConditionsData["dop_info"]

    # Фильтруем нужные записи один раз
    filtered = [
        item for item in dop_info
        if str(item.get("id")) in id_row_user
        and str(item.get("type_machine")) == "2"
    ]

    params_by_id: dict[str, dict] = {}

    for id_str in id_row_user:
        params_by_id[id_str] = {}

        for item in filtered:
            if str(item.get("id")) != id_str:
                continue

            param_name = item.get("parametr_name")
            value = item.get("value")
            unit = item.get("unit_of_measurement")

            params_by_id[id_str][param_name] = {
                "value": value,
                "unit": unit if unit and unit != "-" else None
            }

    return [params_by_id[id_str] for id_str in id_row_user]

async def DopInfo_machine(id_row_user: list[str], lang: str, ConditionsData: dict):
    dop_info = ConditionsData["dop_info"]

    # Фильтруем нужные записи один раз
    filtered = [
        item for item in dop_info
        if str(item.get("id")) in id_row_user
        and str(item.get("type_machine")) == "1"
    ]

    params_by_id: dict[str, dict] = {}

    for id_str in id_row_user:
        params_by_id[id_str] = {}

        for item in filtered:
            if str(item.get("id")) != id_str:
                continue

            param_name = item.get("parametr_name")
            value = item.get("value")
            unit = item.get("unit_of_measurement")

            params_by_id[id_str][param_name] = {
                "value": value,
                "unit": unit if unit and unit != "-" else None
            }

    return [params_by_id[id_str] for id_str in id_row_user]

async def DopInfo_compressor(id_row_user: list[str], lang: str, ConditionsData: dict):
    dop_info = ConditionsData["dop_info"]

    # Фильтруем нужные записи один раз
    filtered = [
        item for item in dop_info
        if str(item.get("id")) in id_row_user
        and str(item.get("type_machine")) == "4"
    ]

    params_by_id: dict[str, dict] = {}

    for id_str in id_row_user:
        params_by_id[id_str] = {}

        for item in filtered:
            if str(item.get("id")) != id_str:
                continue

            param_name = item.get("parametr_name")
            value = item.get("value")
            unit = item.get("unit_of_measurement")

            params_by_id[id_str][param_name] = {
                "value": value,
                "unit": unit if unit and unit != "-" else None
            }

    return [params_by_id[id_str] for id_str in id_row_user]

async def DopInfo_Elevator(id_json_document_elevator: list[str], count_user_elevator: list[int], lang: str):
    params_list_all = []
    for elevator_name, modelCount in zip(id_json_document_elevator, count_user_elevator):
        async with aiofiles.open(f'./Front/static/document/deal_elevator/{elevator_name}.json', encoding='utf-8') as f:
            dataElevator = json.loads(await f.read())

        productName, productCoef = product_name(dataElevator, lang)
        modelName = dataElevator.get('modelName','')
        modelCount = int(modelCount)
        namePhoto = name_photo(modelName)

        # main block
        modelSize = dataElevator.get('modelSize', {})
        capacity_param = dataElevator.get('capacity_param', {})
        otherComponents = dataElevator.get('otherComponents', {})
        sectionElement = dataElevator.get('sectionElement', {})
        onloadElement = dataElevator.get('onloadElement', {})
        metalThickness = dataElevator.get('metalThickness', {})

        # float
        bottom_length = float(modelSize.get('bottom_length', 0))
        top_length = float(modelSize.get('top_length', 0))
        height_length_x = float(modelSize.get('height_length_x', 0))
        height = float(modelSize.get('height', 0))
        unload = float(modelSize.get('unload', 0))
        load = float(modelSize.get('load', 0))
        TransportLength = float(modelSize.get('TransportLength', 0))
        loadCenter = float(modelSize.get('loadCenter', 0))
        unloadCenter = float(modelSize.get('unloadCenter', 0))
        load_x = float(onloadElement.get('load_x', 0))
        unload_x = float(onloadElement.get('unload_x', 0))
        unload_y = float(onloadElement.get('unload_y', 0))
        capacity = float(capacity_param.get('capacity', 0))

        # count / lists
        heightSection = sectionElement.get('heightSection', [])
        topSection = sectionElement.get('topSection', [])
        bottomSection = sectionElement.get('bottomSection', [])
        lengthSection = sectionElement.get('lengthSection', [])
        leteralSection = sectionElement.get('leteralSection', [])
        verticalSection = sectionElement.get('verticalSection', [])

        Total_length_elevator = float(height) + float(top_length) + float(bottom_length)
        efficiency_wheat = float(capacity * float(productCoef))

        if lang == 'ru':
            desc_dop_info = """Выпускаемые нории имеют
                сертификаты соответствия,
                гигиенический сертификат,
                разрешение Ростехнадзора,
                сертификаты СЕ."""
            name_print_CSBC = 'Конвейер ленточный '
            name_print_CSZE = 'Конвейер цепной '
            name_print_CSE = 'Зерновой элеватор '
            name_print_CSCC = 'Конвейер скребковый '
            electricMotor = '(Электродвигатель)'
            Pneumatics = '(Пневматика)'
            Metal = 'Металл'
            Plastic = 'Пластик'
            wheel = "Squirrel Wheel"
            mm = '10мм'
            yes = 'да'
            no = 'нет'
        else:
            desc_dop_info = """The produced bucket elevators have
                certificates of conformity,
                hygienic certificate,
                Rostekhnadzor permission,
                CE certificates."""
            name_print_CSBC = 'Belt conveyor '
            name_print_CSZE = 'Chain conveyor '
            name_print_CSE = 'Grain elevator '
            name_print_CSCC = 'Scraper conveyor '
            electricMotor = '(Electric motor)'
            Pneumatics = '(Pneumatics)'
            Metal = 'Metal'
            Plastic = 'Plastic'
            wheel = "Squirrel Wheel"
            mm = '10mm'
            yes = 'yes'
            no = 'no'

        params_list = {
            'name': modelName,
            'photo': f"http://localhost:8000/off_bot/static/img_machine/{namePhoto}.png",
            'desc_dop_info': desc_dop_info,
            'product_name': productName,
            'namePhoto': namePhoto,
            'modelCount': modelCount,
            'manualElement': modelCount,
            'toolsElement': modelCount,
            'efficiency': format(capacity, '.2f'),
            'efficiency_wheat': format(efficiency_wheat, '.2f'),
            'DrumStep': capacity_param.get('turn', 0),
            'Material': dataElevator.get('material', 0),
            'Reductor': otherComponents.get('reductor', {}).get('name', '') + "(" + MR_country(dataElevator.get('motor_reductor', '')) + ")",
            'Converter': yes if otherComponents.get('converter', {}).get('enable', False) else no,
            'ControlBox': yes if otherComponents.get('controlBox', {}).get('enable', False) else no,
            'controlBoxElement': modelCount if otherComponents.get('controlBox', {}).get('enable', False) else None,
            'sensorPodporBottomElement': modelCount if otherComponents.get('sensorPodporBottom', {}).get('enable', False) else None,
            'sensorSpeedElement': modelCount if otherComponents.get('sensorSpeed', {}).get('enable', False) else None,
            'sensorBeltElement': 4 * modelCount if otherComponents.get('sensorBelt', {}).get('enable', False) else None,
            'sensorPodporElement': modelCount if otherComponents.get('sensorPodpor', {}).get('enable', False) else None,
        }

        if 'CSZE' in modelName:
            elevator_dxf = dataElevator['temporal_data']['dxf']
            elevator_svg = dataElevator['temporal_data']['svg']
            CSZETechnic = "flex" if (
                otherComponents.get('controlBox', {}).get('enable', False) or
                otherComponents.get('sensorPodpor', {}).get('enable', False) or
                otherComponents.get('sensorChain', {}).get('enable', False)) else "none"

            electrical = electricMotor if onloadElement.get('unload', {}).get('type','') == "electrical" else Pneumatics

            params_list.update({
                'name_print': name_print_CSZE + modelName,
                'DefStretchSection': modelCount,
                'DefDriveSection': modelCount,
                'DefCornerSection': 2 * modelCount,
                'DefRevisionWindow': yes,
                'DefHatchesStripping': yes,
                'DefLoadingPorts': yes,
                'chainElement': 2 * modelCount,
                'CSZEBucketElement': modelCount,
                'CSZETechnic': CSZETechnic,
                'motorReductorElement': modelCount,
                'Length_before_loading': format(bottom_length - load_x, '.2f'),
                'TotalLength': format(top_length + bottom_length - height_length_x, '.2f'),
                'TotalLength_mm': format((top_length + bottom_length - height_length_x) * 1000, '.0f'),
                'Length_before_unloading': format(top_length - unload_x, '.2f'),
                'SizeHeightTransport': format(height - unload_y, '.2f'),
                'Elevator_height': format(height, '.2f'),
                'Elevator_height_mm': format(height * 1000, '.0f'),
                'TotalLengthElevator': format(Total_length_elevator, '.2f'),
                'LengthUpperSection': format(top_length, '.2f'),
                'LengthLowerSection': format(bottom_length, '.2f'),
                'Chain_speed': capacity_param.get('speed', 0),
                'Bucket_volume': capacity_param.get('bucket', 0),
                'size_outlet_pipes': dataElevator.get('outletSize', 0),
                'speed_rotation_drum': capacity_param.get('turn', 0),
                'BeltSpeed': capacity_param.get('speed', 0),
                'rated_power_consumption': otherComponents.get('converter', {}).get('kW', 0),
                'BucketMaterial': Metal if dataElevator.get('bucketMaterial', {}) == "bucketMetall" else Plastic,
                'Backward': yes if otherComponents.get('backward', {}).get('enable', False) else no,
                'SensorPodpor': yes if otherComponents.get('sensorPodpor', {}).get('enable', False) else no,
                'ChainSensor': yes if otherComponents.get('sensorChain', {}).get('enable', False) else no,
                'StreetFulfillment': yes if otherComponents.get('streetFulfillment', {}).get('enable', False) else no,
                'passportElement': modelCount if CSZETechnic else None,
                'AddLoad': str(onloadElement.get('load', {}).get('count', '0')),
                'AddUnload': str(onloadElement.get('unload', {}).get('count', '0')) + '\n' + electrical,
                'supporting_structures': str(metalThickness).split("x")[0],
                'not_supporting_structures': str(metalThickness).split("x")[1] if "x" in str(metalThickness) else "",
                'section_element': len(heightSection + topSection + bottomSection) * modelCount,
                'elevator_dxf': elevator_dxf,
                'elevator_svg': elevator_svg,
            })

        elif 'CSE' in modelName:
            elevator_dxf = dataElevator['temporal_data']['dxf']
            elevator_svg = dataElevator['temporal_data']['svg']

            CSETechnic = "flex" if (
                otherComponents.get('controlBox', {}).get('enable', False) or
                otherComponents.get('backward', {}).get('enable', False) or
                otherComponents.get('sensorPodporBottom', {}).get('enable', False) or
                otherComponents.get('sensorSpeed', {}).get('enable', False) or
                otherComponents.get('sensorBelt', {}).get('enable', False)) else "none"

            params_list.update({
                'name_print': name_print_CSE + modelName,
                'DefSuctionConnect': modelCount,
                'DefWindowB': modelCount,
                'DefElevatorShoe': modelCount,
                'DefElevatorHead': modelCount,
                'DefDrumDesign': wheel,
                'bucketElement': modelCount,
                'CSECountMotorReductorElement': modelCount,
                'passportElement': modelCount if CSETechnic else None,
                'CSETechnic': CSETechnic,
                'CSETransportLength': format(height - unload, '.2f'),
                'Elevator_height': format(height, '.2f'),
                'SizeHeightTransport': format(height - unload, '.2f'),
                'Elevator_height_mm': format(height * 1000, '.0f'),
                'CSEBeltSpeed': capacity_param.get('speed', 0),
                'BucketStep': capacity_param.get('step', 0),
                'MetallSection': dataElevator.get('metalThickness', {}).get('tubeT', 0),
                'MetallOther': dataElevator.get('metalThickness', {}).get('headT', 0),
                'BucketMaterial': "Пластик" if dataElevator.get('bucketMaterial', {}) == "bucketPlastic" else "Металл",
                'Motor': otherComponents.get('motor', {}).get('kW', None),
                'Explosion': (
                    "0" if (
                        not otherComponents.get('controlBox', {}).get('enable', False)
                        or not otherComponents.get('backward', {}).get('enable', False)
                        or not otherComponents.get('sensorPodporBottom', {}).get('enable', False)
                        or not otherComponents.get('sensorSpeed', {}).get('enable', False)
                        or not otherComponents.get('sensorBelt', {}).get('enable', False)
                    ) else "1"
                ),
                'Backward': yes if otherComponents.get('backward', {}).get('enable', False) else no,
                'SpeedSensor': yes if otherComponents.get('sensorSpeed', {}).get('enable', False) else no,
                'TapeSensor': yes if otherComponents.get('sensorBelt', {}).get('enable', False) else no,
                'SupportSensorTop': yes if otherComponents.get('sensorPodporTop', {}).get('enable', False) else no,
                'SupportSensorBot': yes if otherComponents.get('sensorPodporBottom', {}).get('enable', False) else no,
                'DrillInBelt': yes if otherComponents.get('drillInBelt', {}).get('enable', False) else no,
                'StreetFulfillment': yes if otherComponents.get('streetFulfillment', {}).get('enable', False) else no,
                'section_element': (len(heightSection) + 2) * modelCount,
                'elevator_dxf': elevator_dxf,
                'elevator_svg': elevator_svg,
            })

        elif 'CSCC' in modelName:
            CSCCTechnic = "flex" if (
                otherComponents.get('controlBox', {}).get('enable', False) or
                otherComponents.get('converter', {}).get('enable', False) or
                otherComponents.get('sensorSpeed', {}).get('enable', False)) else "none"

            params_list.update({
                'name_print': name_print_CSCC + modelName,
                'CSCCDefSuctionConnect': modelCount,
                'DefWindow': modelCount,
                'CSCCScraperMaterial': Plastic,
                'DefStretchSection': modelCount,
                'DefDriveSection': modelCount,
                'CSCCTechnic': CSCCTechnic,
                'chainElement': modelCount,
                'CSCCBucketElement': modelCount,
                'motorReductorElement': modelCount,
                'passportElement': modelCount if CSCCTechnic else None,
                'TransportLength': format((TransportLength - (unload + load)), '.2f'),
                'Length': format(TransportLength, '.2f'),
                'Length_mm': format(TransportLength*1000, '.0f'),
                'LengthAxis': format((TransportLength - (loadCenter + unloadCenter)), '.2f'),
                'BeltSpeed': capacity_param.get('speed', ''),
                'ScraperStep': capacity_param.get('step', ''),
                'bodyT': metalThickness.get('bodyT', ''),
                'capT': metalThickness.get('capT', ''),
                'liningT': metalThickness.get('liningT', ''),
                'Motor': otherComponents.get('motor', {}).get('kW', None),
                'SpeedSensor': yes if otherComponents.get('sensorSpeed', {}).get('enable', False) else no,
                'SupportSensorTop': yes if otherComponents.get('sensorPodpor', {}).get('enable', False) else no,
                'Backload': mm if len(sectionElement.get('leteralSection', [])) != 0 else no,
                'DoubleSideBackload': True if sectionElement.get('doubleSideLateral', False) else False,
                'StreetFulfillment': yes if otherComponents.get('streetFulfillment', {}).get('enable', False) else no,
                'Vertical': f"{len(sectionElement.get('verticalSection', []))}шт" if len(sectionElement.get('verticalSection', [])) != 0 else no,
                'section_element': len(lengthSection + leteralSection + verticalSection) * modelCount,
            })

        elif 'CSBC' in modelName:
            CSBCTechnic = "flex" if (
                otherComponents.get('controlBox', {}).get('enable', False) or
                otherComponents.get('converter', {}).get('enable', False) or
                otherComponents.get('sensorSpeed', {}).get('enable', False)) else "none"

            params_list.update({
                'name_print': name_print_CSBC + modelName,
                'DefStretchSection': modelCount,
                'DefDriveSection': modelCount,
                'OneChainElement': modelCount,
                'CSBCTechnic': CSBCTechnic,
                'motorReductorElement': modelCount,
                'passportElement': modelCount if CSBCTechnic else None,
                'TransportLength': format((TransportLength - (unload + load)), '.2f'),
                'Length': format(TransportLength, '.2f'),
                'Length_mm': format(TransportLength*1000, '.0f'),
                'LengthAxis': format((TransportLength - (loadCenter + unloadCenter)), '.2f'),
                'SpeedSensor': yes if otherComponents.get('sensorSpeed', {}).get('enable', False) else no,
                'SupportSensorTop': yes if otherComponents.get('sensorPodpor', {}).get('enable', False) else no,
                'StreetFulfillmentUpper': yes if otherComponents.get('streetFulfillmentUpper', {}).get('enable', False) else no,
                'StreetFulfillmentBottom': yes if otherComponents.get('streetFulfillmentBottom', {}).get('enable', False) else no,
                'AddUnloadTENS': yes if modelSize.get('addUnloadTENS', {}) else no,
                'CSBCVulcanBonding': yes if otherComponents.get('vulcanBonding', {}).get('enable', False) else no,
                'AddLoad': str(onloadElement.get('load', {}).get('count', '0')),
                'bodyT': metalThickness.get('bodyT', ''),
                'capT': metalThickness.get('capT', ''),
                'CSEBeltSpeed': capacity_param.get('speed', 0),
                'Motor': otherComponents.get('motor', {}).get('kW', None),
                'section_element': len(lengthSection) * modelCount,
            })

        params_list_all.append(params_list)
    return params_list_all

async def DopInfo_laboratory(id_row_user: list[str], lang: str, ConditionsData: dict):
    dop_info = ConditionsData["dop_info"]
    # Фильтруем нужные записи один раз
    filtered = [
        item for item in dop_info
        if str(item.get("id")) in id_row_user
        if str(item.get("type_machine")) == "9"
    ]

    params_by_id: dict[str, dict] = {}

    for id_str in id_row_user:
        params_by_id[id_str] = {}

        for item in filtered:
            if str(item.get("id")) != id_str:
                continue

            param_name = item.get("parametr_name")
            value = item.get("value")
            unit = item.get("unit_of_measurement")

            params_by_id[id_str][param_name] = {
                "value": value,
                "unit": unit if unit and unit != "-" else None
            }

    return [params_by_id[id_str] for id_str in id_row_user]
