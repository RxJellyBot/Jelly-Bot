import warnings


def warn_keys_not_used(model_name, unused_keys):
    warnings.warn(f"Keys provided not used to construct `{model_name}`. - {unused_keys}")


def warn_field_key_not_found_for_json_key(model_name, json_key, action):
    warnings.warn(f"Json key ({json_key}) existed, but no corresponding key found in the model `{model_name}`. "
                  f"{action} action aborted.")


def warn_action_failed_json_key(model_name, json_key, action):
    warnings.warn(f"Attempted to {action} value using the json key ({json_key}) which "
                  f"does not belong to this model ({model_name}).")
