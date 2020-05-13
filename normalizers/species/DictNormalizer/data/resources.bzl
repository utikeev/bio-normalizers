load('@bazel_tools//tools/build_defs/repo:http.bzl', 'http_archive')

def ncbi_taxonomy(date, sha256):
    # Fetch taxonomy dump from the selected date.
    # SHA256 of .zip should be provided as an argument of the macro.

    BUILD_FILE = "exports_files(glob(['**/*']))"

    http_archive(
        name = 'ncbi_taxonomy',
        urls = ['https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_archive/taxdmp_{}.zip'.format(date)],
        sha256 = sha256,
        build_file_content = BUILD_FILE,
    )
