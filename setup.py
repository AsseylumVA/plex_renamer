from setuptools import setup, find_packages

setup(
    name='plex_renamer',
    version='0.1.0',
    packages=find_packages(),
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'plex_renamer = plex_renamer.gui_plex_renamer_tk:main',  # если есть main()
        ],
    },
)
