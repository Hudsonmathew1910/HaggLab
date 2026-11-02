"""
Static files storage: WhiteNoise's compressed, hashed files, but a path that is not in the manifest falls back to its
plain URL instead of raising an error.

Why: the admin theme (Jazzmin) writes {% static 'vendor/bootswatch' %}, a folder, not a file. Folders are never in
the manifest, so the strict default crashed every admin page after login whenever DEBUG was off (production).
"""
from whitenoise.storage import CompressedManifestStaticFilesStorage


class StaticStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
