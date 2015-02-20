from setuptools import setup, find_packages

setup(
    name='aleph_crawlers',
    version='0.2',
    description="Crawlers for the aleph system",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://grano.cc',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points={
        'aleph.crawlers': [
            'rigzone = aleph_crawlers.news.rigzone:RigZoneCrawler',
            'allafrica = aleph_crawlers.news.allafrica:AllAfricaCrawler',
            'africacheck = aleph_crawlers.news.africacheck:AfricaCheckCrawler',
            'amabhungane = aleph_crawlers.news.amabhungane:AmaBhunganeCrawler',
            'edgar = aleph_crawlers.public.edgar:EdgarCrawler',
            'openoil = aleph_crawlers.public.openoil:OpenOilCrawler',
            'wbdocs = aleph_crawlers.public.wb_docs:WorldBankDocsCrawler',
            'ifcdocs = aleph_crawlers.public.ifc_docs:IFCDocsCrawler',
            'saflii = aleph_crawlers.public.saflii:SafliiCrawler'
        ]
    },
    tests_require=[]
)
