from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
from typing import Dict, List

from bson import ObjectId

from mongodb.factory import RootUserManager, ProfileManager, ChannelManager
from models import ChannelProfileConnectionModel, OnPlatformUserModel, ChannelModel, set_uname_cache
from extutils.timing import exec_timing_result
from extutils.emailutils import MailSender


def _perform_existence_check_(set_name_to_cache: bool):
    list_prof_conn = list(ProfileManager.get_available_connections())

    def fn():
        dict_onplat_oids = RootUserManager.get_root_to_onplat_dict()
        dict_onplat_data = RootUserManager.get_onplat_data_dict()
        dict_channel = ChannelManager.get_channel_dict([p.channel_oid for p in list_prof_conn], accessbible_only=True)

        with ThreadPoolExecutor(max_workers=4, thread_name_prefix="ExstCheck") as executor:
            futures = [
                executor.submit(_check_on_prof_conn_, d, set_name_to_cache, dict_onplat_oids, dict_onplat_data,
                                dict_channel)
                for d in list_prof_conn
            ]

            # Non-lock call & Free resources when execution is done
            executor.shutdown(False)

            for completed in futures:
                completed.result()

    print(f"Performing user channel existence check on {len(list_prof_conn)} connections...")

    result = exec_timing_result(fn)

    print(f"User channel existence check completed in {result.execution_ms:.2f} ms.")


def _check_on_prof_conn_(
        prof_conn: ChannelProfileConnectionModel,
        set_name_to_cache: bool,
        dict_onplat_oids: Dict[ObjectId, List[ObjectId]],
        dict_onplat_data: Dict[ObjectId, OnPlatformUserModel],
        dict_channel: Dict[ObjectId, ChannelModel]):
    oid_user = prof_conn.user_oid
    list_onplat_oids = dict_onplat_oids.get(oid_user)
    if not list_onplat_oids:
        return

    model_channel = dict_channel.get(prof_conn.channel_oid)
    if not model_channel:
        return

    attempts = 0
    attempts_allowed = len(list_onplat_oids)

    for oid_onplat in list_onplat_oids:
        model_onplat = dict_onplat_data.get(oid_onplat)
        if not model_onplat:
            MailSender.send_email_async(
                f"Missing OnPlatform data of data ID: {oid_onplat}<br>"
                f"Root User ID: {prof_conn.user_oid}",
                subject="Missing OnPlatform Data in Root User Model"
            )
            continue

        n = model_onplat.get_name(model_channel)

        if n:
            if set_name_to_cache:
                set_uname_cache(model_onplat.id, n)

            break

        attempts += 1

    if attempts >= attempts_allowed:
        ProfileManager.mark_unavailable_async(model_channel.id, oid_user)


def perform_existence_check(set_name_to_cache: bool):
    Thread(target=_perform_existence_check_, args=(set_name_to_cache,)).start()
