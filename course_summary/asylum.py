    # items = modulestore().get_items(course_key)
    # for item in items:
    #     fields, block_type = serialize_item(item)

    #     for field_name, value in fields.items():
    #         fields[field_name] = coerce_types(value)

    # course_details_serializer = CourseDetailsSerializer(course_details)

    # course_grading_serializer = CourseGradingModelSerializer(course_grading)

    # sections = course_outline_data.sections

    # store = modulestore()

    # with store.branch_setting(ModuleStoreEnum.Branch.published_only):
    #     course_block = store.get_course(course_key, depth=0, lazy=False)

    # course_assets = store.get_all_asset_metadata(course_key, maxresults=-1, asset_type=None)