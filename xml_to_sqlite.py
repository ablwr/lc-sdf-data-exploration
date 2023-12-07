import lxml.etree as ET
from lxml.etree import tostring
import os
import sqlite3
from uuid import uuid4

# Function to create SQLite tables
def create_tables(conn):
    cursor = conn.cursor()

    # Create main table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS main (
            id TEXT PRIMARY KEY,
            titleName TEXT,
            shortName TEXT,
            draftStatus TEXT,
            category TEXT,
            gdfrGenre TEXT,
            gdfrComposition TEXT,
            gdfrBasis TEXT,
            gdfrForm TEXT,
            gdfrConstraint TEXT,
            date TEXT,
            fullName TEXT,
            keywords TEXT,
            description TEXT,
            productionPhase TEXT,
            shortDescription TEXT,
            signifiersGroup TEXT,
            experience TEXT,
            preference TEXT,
            adoption TEXT,
            disclosure TEXT,
            documentation TEXT,
            externalDependencies TEXT,
            licensingAndPatents TEXT,
            selfDocumentation TEXT,
            techProtection TEXT,
            transparency TEXT,
            qualityAndFunctionalityFactors TEXT,
            general TEXT,
            history TEXT
        )
    ''')

    # Create relationships table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id TEXT PRIMARY KEY,
            main_id TEXT,
            typeOfRelationship TEXT,
            relatedTo_id TEXT,
            relatedTo_shortName TEXT,
            relatedTo_titleName TEXT,
            relatedTo_comment TEXT,
            FOREIGN KEY (main_id) REFERENCES main (id)
        )
    ''')

    # Create citations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citations (
            id TEXT PRIMARY KEY,
            main_id TEXT,
            link TEXT,
            tag TEXT,
            comment TEXT,
            FOREIGN KEY (main_id) REFERENCES main (id)
        )
    ''')
    
    conn.commit()

# Function to insert data into main table
def insert_main_data(conn, data):
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR IGNORE INTO main (
        id,
        titleName,
        shortName,
        draftStatus,
        category,
        gdfrGenre,
        gdfrComposition,
        gdfrBasis,
        gdfrForm,
        gdfrConstraint,
        date,
        fullName,
        keywords,
        description,
        productionPhase,
        shortDescription,
        signifiersGroup,
        experience,
        preference,
        adoption,
        disclosure,
        documentation,
        externalDependencies,
        licensingAndPatents,
        selfDocumentation,
        techProtection,
        transparency,
        qualityAndFunctionalityFactors,
        general,
        history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['id'],
        data['titleName'],
        data['shortName'],
        str(data['draftStatus'].text),
        str(data['category']),
        data['gdfrGenre'],
        data['gdfrComposition'],
        str(data['gdfrBasis']),
        str(data['gdfrForm']),
        str(data['gdfrConstraint']),
        data['date'].text,
        data['fullName'].text,
        " ".join(data['keywords'].split()),
        data['description'],
        data['productionPhase'],
        data['shortDescription'],
        data['signifiersGroup'],
        data['experience'],
        data['preference'],
        data['adoption'],
        data['disclosure'],
        data['documentation'],
        data['externalDependencies'],
        data['licensingAndPatents'],
        data['selfDocumentation'],
        data['techProtection'],
        data['transparency'],
        " ".join(data['qualityAndFunctionalityFactors'].split()),
        data['general'],
        data['history']
    ))

    conn.commit()

# Function to insert data into relationships table
def insert_relationships_data(conn, main_id, relationship_data):
    cursor = conn.cursor()

    for relationship in relationship_data:
        cursor.execute('''
            INSERT OR IGNORE INTO relationships (id, main_id, typeOfRelationship,
            relatedTo_id, relatedTo_shortName, relatedTo_titleName, relatedTo_comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            relationship['id'],
            main_id,
            relationship['typeOfRelationship'].text,
            relationship['relatedTo']['id'],
            relationship['relatedTo']['shortName'],
            relationship['relatedTo']['titleName'],
            relationship['relatedTo']['comment']
        ))

    conn.commit()

# Function to insert data into citations table
def insert_citations_data(conn, main_id, reference_data):
    cursor = conn.cursor()

    for ref in reference_data:
        cursor.execute('''
            INSERT OR IGNORE INTO citations (id, main_id, link, tag, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            ref['id'],
            main_id,
            ref['link'],
            ref['tag'],
            ref['comment']
        ))

    conn.commit()

# helper
def or_blank(s):
    return "" if s is None else s.text

def or_blank_parsed(s):
    return "" if s is None else ''.join(s.itertext())

def or_blank_xml(s):
    return "" if s is None else ''.join(s.itertext())

# Function to parse XML file and insert data into SQLite tables
def parse_xml_file(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    main_data = {
        'id': root.attrib.get('id'),
        'titleName': root.attrib.get('titleName'),
        'shortName': root.attrib.get('shortName'),
        'draftStatus': root.find('.//fdd:draftStatus', namespaces=root.nsmap),
        'category': or_blank(root.find('.//fdd:category', namespaces=root.nsmap)),
        'gdfrGenre': or_blank(root.find('.//fdd:gdfrGenre', namespaces=root.nsmap)),
        'gdfrComposition': or_blank(root.find('.//fdd:gdfrComposition', namespaces=root.nsmap)),
        'gdfrBasis': or_blank(root.find('.//fdd:gdfrBasis', namespaces=root.nsmap)),
        'gdfrForm': or_blank(root.find('.//fdd:gdfrForm', namespaces=root.nsmap)),
        'gdfrConstraint': or_blank(root.find('.//fdd:gdfrConstraint', namespaces=root.nsmap)),
        'date': root.find('.//fdd:date', namespaces=root.nsmap),
        'fullName': root.find('.//fdd:fullName', namespaces=root.nsmap),
        'keywords': or_blank_parsed(root.find('.//fdd:keywords', namespaces=root.nsmap)),
        'description': or_blank_parsed(root.find('.//fdd:description', namespaces=root.nsmap)),
        'productionPhase': or_blank_parsed(root.find('.//fdd:productionPhase', namespaces=root.nsmap)),
        'shortDescription': or_blank_parsed(root.find('.//fdd:shortDescription', namespaces=root.nsmap)),
        # TODO may be better to break into subvalues / table.
        'signifiersGroup': or_blank(root.find('.//fdd:signifiersGroup', namespaces=root.nsmap)),
        'experience': or_blank_parsed(root.find('.//fdd:experience', namespaces=root.nsmap)),
        'preference': or_blank_parsed(root.find('.//fdd:preference', namespaces=root.nsmap)),
        'adoption': or_blank_parsed(root.find('.//fdd:adoption', namespaces=root.nsmap)),
        'disclosure': or_blank_parsed(root.find('.//fdd:disclosure', namespaces=root.nsmap)),
        'documentation': or_blank_parsed(root.find('.//fdd:documentation', namespaces=root.nsmap)),
        'externalDependencies': or_blank_parsed(root.find('.//fdd:externalDependencies', namespaces=root.nsmap)),
        'licensingAndPatents': or_blank_parsed(root.find('.//fdd:licensingAndPatents', namespaces=root.nsmap)),
        'selfDocumentation': or_blank_parsed(root.find('.//fdd:selfDocumentation', namespaces=root.nsmap)),
        'techProtection': or_blank_parsed(root.find('.//fdd:techProtection', namespaces=root.nsmap)),
        'transparency': or_blank_parsed(root.find('.//fdd:transparency', namespaces=root.nsmap)),
        # TODO for this one, too.
        'qualityAndFunctionalityFactors': or_blank_parsed(root.find('.//fdd:qualityAndFunctionalityFactors', namespaces=root.nsmap)),
        'general': or_blank_parsed(root.find('.//fdd:general', namespaces=root.nsmap)),
        'history': or_blank_parsed(root.find('.//fdd:history', namespaces=root.nsmap))
    }

    conn = sqlite3.connect('fdd_database.db')
    create_tables(conn)
    insert_main_data(conn, main_data)

    relationship_data = []
    for relationship_elem in root.findall('.//fdd:relationships/fdd:relationship', namespaces=root.nsmap):
        relationship = {
            'id': str(uuid4()),
            'typeOfRelationship': relationship_elem.find('fdd:typeOfRelationship', namespaces=root.nsmap),
            'relatedTo': {
                'id': or_blank(relationship_elem.find('fdd:relatedTo/fdd:id', namespaces=root.nsmap)),
                'shortName': or_blank(relationship_elem.find('fdd:relatedTo/fdd:shortName', namespaces=root.nsmap)),
                'titleName': or_blank(relationship_elem.find('fdd:relatedTo/fdd:titleName', namespaces=root.nsmap)),
                'comment': or_blank(relationship_elem.find('fdd:relatedTo/fdd:comment', namespaces=root.nsmap)),
            }
        }
        relationship_data.append(relationship)

    insert_relationships_data(conn, main_data['id'], relationship_data)

    citation_data = []
    for citation_elem in root.findall('.//fdd:urlReference', namespaces=root.nsmap):
        reference = {
            'id': str(uuid4()),
            'link': or_blank_parsed(citation_elem.find('link', namespaces=root.nsmap)),
            'tag': or_blank_parsed(citation_elem.find('tag', namespaces=root.nsmap)),
            'comment': or_blank_parsed(citation_elem.find('comment', namespaces=root.nsmap))
        }
        citation_data.append(reference)

    insert_citations_data(conn, main_data['id'], citation_data)
    conn.close()

# Specify the directory containing XML files
xml_files_directory = 'fddXML/'

# Iterate over XML files in the directory and process each file
for filename in os.listdir(xml_files_directory):
    if filename.endswith('.xml'):
        print(filename)
        xml_file_path = os.path.join(xml_files_directory, filename)
        if os.path.getsize(xml_file_path) > 0:
            parse_xml_file(xml_file_path)


