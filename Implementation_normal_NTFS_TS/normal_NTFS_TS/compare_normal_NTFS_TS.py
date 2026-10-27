from normal_NTFS_TS import normal_NTFS_TS
from normal_NTFS_TS_FT import normal_NTFS_TS_FT
from normal_NTFS_TS_CR import normal_NTFS_TS_CR

def identical_list_TS(list_1: list[list[str]],list_1_name: str, list_2: list[list[str]], list_2_name: str): 
    if all(TS in list_2 for TS in list_1) and all(TS in list_1 for TS in list_2):
        print(f"{list_1_name} and {list_2_name} are identical.")
    else:
        print(f"{list_1_name} and {list_2_name} are NOT identical.")

if __name__ == "__main__":
    
    identical_list_TS(
        list_1=normal_NTFS_TS,
        list_1_name="normal_NTFS_TS",
        list_2=normal_NTFS_TS_FT,
        list_2_name="normal_NTFS_TS_FT"
    )

    identical_list_TS(
        list_1=normal_NTFS_TS,
        list_1_name="normal_NTFS_TS",
        list_2=normal_NTFS_TS_CR,
        list_2_name="normal_NTFS_TS_CR"
    )

    identical_list_TS(
            list_1=normal_NTFS_TS_FT,
            list_1_name="normal_NTFS_TS_FT",
            list_2=normal_NTFS_TS_CR,
            list_2_name="normal_NTFS_TS_CR"
    )




