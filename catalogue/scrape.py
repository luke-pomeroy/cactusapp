from bs4 import BeautifulSoup
import requests, re
from catalogue.models import *

def speciesscrape(url):
    webpage = requests.get(url)
    html = webpage.text
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    photos = []
    main_photo = soup.find(id='main_photo_container')
    other_photos = soup.findAll(class_='plant_main_sec_photo_area top_image')
    species = soup.find('span', class_='plant_main_scientific_name_header').get_text()    
    family = soup.select("span.plant_family_title > a")[0].text.strip()
    main_author = soup.find('span', class_='plant_main_author_header').get_text() 
    main_subheader = soup.find('span', class_='plant_main_subheader').get_text()
    main_photo_url = main_photo.find('img')
    if main_photo_url:
        main_photo_link = {'src': 'http://www.llifle.com/' + main_photo_url['src'], 'caption': main_photo.find(class_='plant_main_photo_description').get_text()}
        photos.append(main_photo_link)

    if not other_photos == '<div id="plant_main_sec_photo_area top_image"></div>':
        for other_photo in other_photos:
            opct = ''
            for other_photo_caption in other_photo.findAll(class_='photo_m_description'):
                opct = f'{opct} {other_photo_caption.text}'
            
            other_photo_link = {'src': 'http://www.llifle.com/' + other_photo.find('img')['src'].replace('_m.j', '_l.j'), 'caption': opct}
            photos.append(other_photo_link)

    description_sections = soup.findAll('p', class_=[
                                    'Description_Sheet_Origin_and_Habitat',
                                    'Description_Sheet_Description',
                                    'Description_Sheet_Note',
                                    'Description_Sheet_Bibliography',
                                    'Description_Sheet_Cultivation_and_Propagation',
                                    ])
    for section in description_sections: 
        description_group=section.attrs.get("class")[1]
        descriptions = section.find_all('b', text=re.compile(r':| - |- '))
        for description in descriptions:
            for index, sib in enumerate(description.next_siblings):
                if index ==0:
                    label = description.get_text()
                    description_text = ''
                    data=''
                if sib.name == 'br' and (sib.next_sibling in descriptions or sib.next_sibling == ' - ' or sib.next_sibling == '- '):
                    break
                else:
                    description_text = f'{description_text}{sib}'
                data = {'term_title': label.replace(': ', '').replace(':', ''), 'text': description_text}
            if data:    
                results.append(data)
    new_species = Species(scientific_name= species, family=family, author=main_author, 
    source=main_subheader, genus=species.split(' ',1)[0], specific_epithet=species.split(' ',1)[1], url=url)
    new_species.save()
    print(results)
    for index, result in enumerate(results):
        print("Another one: ")
        print(result['text'])
        new_description = SpeciesDescription(species=new_species, description= result['text'],
        descript_type=result['term_title'], descript_group=description_group, order = index)
        new_description.save()  
    for index, photo in enumerate(photos):
        new_photo = Photo(content_object=new_species, image_url=photo['src'], caption=photo['caption'], order=index)
        new_photo.save()

    return new_species
    #change this to pass the objects, then save in the main view so we can check for existing species