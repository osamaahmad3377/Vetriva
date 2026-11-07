"""Build one page per service (service-<slug>.html).

The header, footer and WhatsApp button are copied from index.html, so after changing those on the
home page, re-run:

    python3 tools/build_service_pages.py
    python3 tools/build_product_pages.py

The wording is general information for pet owners. Have your vets review it, and add anything specific
to Vetriva (opening times, prices, equipment) before the site goes live.
"""
import html
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
WHATSAPP = '923239737896'  # TODO: replace with the clinic's real WhatsApp number

ICONS = {
    'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    'plus': '<rect x="3" y="3" width="18" height="18" rx="5"/><path d="M12 8v8M8 12h8"/>',
    'pulse': '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    'leaf': '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.2-6.1 2.4-.5 4.8-2 5.8-3.9"/>',
    'syringe': '<path d="m18 2 4 4M17 7l3-3M19 9 8.7 19.3a2.4 2.4 0 0 1-3.4 0l-.6-.6a2.4 2.4 0 0 1 0-3.4L15 5M9 11l4 4M5 19l-3 3M14 4l6 6"/>',
    'tooth': '<path d="M12 5.5c-1.5-2-4.5-2.5-6.5-1S3 9 4 12c.7 2 1 4 1.5 6 .3 1.5 1 2.5 2 2.5s1.5-1 2-3c.4-1.5 1-2.5 2.5-2.5s2.1 1 2.5 2.5c.5 2 1 3 2 3s1.7-1 2-2.5c.5-2 .8-4 1.5-6 1-3 .5-6-1.5-7.5s-5-1-6.5 1z"/>',
    'flask': '<path d="M9 3h6M10 3v6.5L4.5 19A1.5 1.5 0 0 0 5.8 21h12.4a1.5 1.5 0 0 0 1.3-2L14 9.5V3"/><path d="M7 15h10"/>',
    'scan': '<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>',
    'heart': '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7z"/>',
    'chip': '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    'scissors': '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4 8.1 15.9M14.5 14.5 20 20M8.1 8.1 12 12"/>',
    'bowl': '<path d="M3 11h18a9 9 0 0 1-18 0Z"/><path d="M8 7.5c.4-1.4 1.4-2.2 3-2.4M13.5 6.5c.4-1 1.3-1.6 2.8-1.7"/>',
    'paw': '<ellipse cx="5.4" cy="10.4" rx="2.1" ry="2.6"/><ellipse cx="9.5" cy="5.9" rx="2.1" ry="2.7"/><ellipse cx="14.5" cy="5.9" rx="2.1" ry="2.7"/><ellipse cx="18.6" cy="10.4" rx="2.1" ry="2.6"/><path d="M12 11.6c-3 0-6.1 3.7-6.1 6.3 0 1.7 1.3 2.5 2.9 2.5 1.3 0 2.1-.7 3.2-.7s1.9.7 3.2.7c1.6 0 2.9-.8 2.9-2.5 0-2.6-3.1-6.3-6.1-6.3z"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    'calendar': '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    'alert': '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    'check': '<path d="M20 6 9 17l-5-5"/>',
}

FOCUS = {  # slug -> object-position of the cover photo
    'wellness-examination': '35% 50%', 'vaccination': '50% 35%', 'deworming': '50% 40%', 'microchipping': '50% 40%',
    'surgery': '45% 45%', 'neutering-spaying': '50% 45%', 'dentistry': '50% 45%', 'exotic-animals': '50% 40%',
    'laboratory': '50% 50%', 'digital-x-rays': '50% 45%', 'ultrasound': '35% 50%', 'mri-ct-scan': '70% 50%',
    'ecg-eco': '50% 40%', 'diet-management': '50% 60%', 'pet-food': '50% 50%', 'grooming': '50% 50%',
}

GROUPS = ['Preventive Care', 'Surgery & Treatment', 'Diagnostics', 'Nutrition & Care']

# slug -> everything shown on the page. Order here is the order of the Services menu.
SERVICES = [
    dict(slug='wellness-examination', name='Wellness Examination', group=0, icon='shield',
         tagline='A thorough head-to-tail check-up to keep your pet healthy.',
         intro='A regular wellness exam is the best way to catch small problems before they become big ones. Our vets examine your pet from nose to tail, talk through their diet, behaviour and routine, and give you clear, practical advice.',
         includes=['Full physical examination, including eyes, ears, teeth, skin, heart and lungs',
                   'Weight and body condition check',
                   'Review of vaccinations, parasite control and diet',
                   'Advice on behaviour, exercise and home care',
                   'A plan for any follow-up tests or treatment'],
         when=[('Yearly check-up', 'Healthy adult pets benefit from a check-up at least once a year.'),
               ('New pet', 'Start your puppy, kitten or newly adopted pet off on the right foot.'),
               ('Something seems off', 'Changes in appetite, energy, weight, toilet habits or behaviour.')],
         steps=[('Book your visit', 'Choose a time online, on WhatsApp or by phone.'),
                ('Meet your vet', 'A calm, unhurried examination, and time for all your questions.'),
                ('Go home with a plan', 'Clear next steps, in plain words, for your pet’s health.')],
         faqs=[('How often should my pet have a check-up?', 'Most healthy adult pets should be seen at least once a year. Puppies, kittens, seniors and pets with health conditions often need to be seen more often. Your vet will advise what suits your pet.'),
               ('What should I bring?', 'Any previous medical or vaccination records, a list of the food and medicines your pet currently has, and a fresh stool sample if you can. Keep dogs on a leash and cats in a secure carrier.'),
               ('Can I ask about a specific worry?', 'Yes. Tell us at booking or at the start of the visit and we will make time for it.')]),
    dict(slug='vaccination', name='Vaccination', group=0, icon='syringe',
         tagline='Protection against serious, preventable diseases.',
         intro='Vaccines protect your pet from serious infectious diseases and help keep other pets safe too. We create a vaccination schedule that fits your pet’s age, lifestyle and health, and keep it on track with reminders.',
         includes=['Core vaccines for dogs and cats, chosen by your vet',
                   'Rabies vaccination',
                   'Health check before every vaccine',
                   'A vaccination record for your pet',
                   'Reminders when boosters are due'],
         when=[('Puppies and kittens', 'A series of vaccines in the first months of life, followed by boosters.'),
               ('Yearly boosters', 'Keep your adult pet’s protection up to date.'),
               ('Travel and boarding', 'Many boarding places and travel plans need up-to-date vaccination records.')],
         steps=[('Quick health check', 'Your vet makes sure your pet is well enough to be vaccinated.'),
                ('Vaccination', 'A quick, gentle injection, with treats and reassurance.'),
                ('Record and reminders', 'We update your pet’s record and tell you when the next one is due.')],
         faqs=[('When should my puppy or kitten start vaccinations?', 'Usually from around six to eight weeks old, with boosters a few weeks apart. Your vet will give you the exact schedule for your pet.'),
               ('Are there side effects?', 'Most pets feel fine. Some are a little sleepy or sore for a day. Rarely, pets can have a stronger reaction, so call us straight away if you are worried.'),
               ('My pet missed a booster. What now?', 'Do not worry. Book a visit and your vet will tell you whether a single booster is enough or the course needs to be restarted.')]),
    dict(slug='deworming', name='Deworming', group=0, icon='leaf',
         tagline='Safe, regular parasite control for a healthy gut and a happy home.',
         intro='Worms and other parasites are common in pets and can affect their health and sometimes yours. Regular deworming, with the right product at the right dose, keeps your pet comfortable and your family protected.',
         includes=['Weight check so the dose is right for your pet',
                   'Treatment chosen for your pet’s age and lifestyle',
                   'Advice on a regular deworming schedule',
                   'Tips on hygiene and preventing re-infection',
                   'Stool test when needed'],
         when=[('Puppies and kittens', 'Young animals are often dewormed more frequently.'),
               ('Regular prevention', 'Adult pets need to be dewormed on a regular schedule.'),
               ('Warning signs', 'Weight loss, a swollen belly, diarrhoea, or worms seen in stool or vomit.')],
         steps=[('Weigh and check', 'We weigh your pet so the dose is exactly right.'),
                ('Treatment', 'Tablets or liquid, chosen by your vet.'),
                ('Schedule', 'We tell you when to repeat, and set a reminder.')],
         faqs=[('How often should I deworm my pet?', 'It depends on age, lifestyle and the product used. Your vet will set a schedule, and will usually recommend more frequent treatment for puppies and kittens.'),
               ('Can I use a shop-bought dewormer?', 'Some work well, but the right product and dose depend on your pet’s weight, age and health. It is best to ask your vet first.'),
               ('Can I catch worms from my pet?', 'Some pet worms can infect people, especially children. Regular deworming and good hygiene greatly reduce the risk.')]),
    dict(slug='microchipping', name='Microchipping', group=0, icon='chip',
         tagline='A permanent way to get a lost pet back home.',
         intro='A microchip is a tiny chip, about the size of a grain of rice, placed just under your pet’s skin. If your pet is ever lost, a vet or shelter can scan the chip and use your details to contact you.',
         includes=['Quick microchip implant, done during a visit',
                   'Scan check to confirm the chip works',
                   'Your contact details linked to the chip number',
                   'A chip number record for your files',
                   'Advice on keeping your details up to date'],
         when=[('Puppies and kittens', 'Chipping young pets early gives lifelong peace of mind.'),
               ('Adopted pets', 'Make sure a rescued or adopted pet can always be identified.'),
               ('Travel', 'Many travel plans require a microchip.')],
         steps=[('Book a short visit', 'Often it can be done alongside a vaccination.'),
                ('Implant', 'A quick injection under the skin, similar to a vaccine.'),
                ('Register your details', 'We help you record your contact details against the chip.')],
         faqs=[('Does it hurt?', 'Most pets barely notice. It feels like a normal injection and takes a few seconds.'),
               ('Is it a tracking device?', 'No. A microchip has no battery and no GPS. It holds a number that is read by a scanner when your pet is found.'),
               ('What if I move or change my phone number?', 'Update your details as soon as they change, otherwise the chip cannot help bring your pet home. Ask us if you are unsure how.')]),

    dict(slug='surgery', name='Surgery', group=1, icon='plus',
         tagline='Safe, carefully monitored surgery with a focus on comfort and recovery.',
         intro='When your pet needs an operation, we explain every step beforehand and look after them closely before, during and after the procedure. Our team monitors anaesthesia and pain control throughout, so your pet recovers as comfortably as possible.',
         includes=['Pre-surgical examination and, where needed, blood tests',
                   'Anaesthesia with careful monitoring',
                   'Soft-tissue and other surgical procedures, as advised by your vet',
                   'Pain relief during and after the operation',
                   'Written aftercare advice and a follow-up check'],
         when=[('Planned procedures', 'Lump removal, wound repair and other operations your vet recommends.'),
               ('Injury or illness', 'When surgery is the best way to help your pet recover.'),
               ('Second opinion', 'Bring your pet’s records if you would like our vets’ advice.')],
         steps=[('Consultation', 'Your vet examines your pet and explains the options.'),
                ('Surgery day', 'Fasting instructions, a calm drop-off and close monitoring.'),
                ('Recovery', 'Aftercare instructions and a check-up to make sure healing goes well.')],
         faqs=[('Does my pet need to fast before surgery?', 'Usually yes. We will tell you exactly when to take food and water away. Follow our instructions carefully, as it makes the anaesthetic safer.'),
               ('Is anaesthesia safe?', 'Every anaesthetic carries some risk, but modern drugs and careful monitoring make it very safe for most pets. Your vet will check your pet beforehand and discuss any extra risks.'),
               ('How long is recovery?', 'It depends on the procedure. Your vet will tell you what to expect, how to care for the wound and when to bring your pet back.')]),
    dict(slug='neutering-spaying', name='Neutering & Spaying', group=1, icon='shield',
         tagline='A routine procedure with lifelong health benefits.',
         intro='Neutering (males) and spaying (females) prevent unwanted litters and can lower the risk of some health problems. Your vet will talk through the best timing for your pet’s species, breed and size.',
         includes=['Pre-operative check-up',
                   'Safe anaesthesia with monitoring',
                   'Pain relief and aftercare supplies',
                   'Clear home-care instructions, including activity and wound care',
                   'Follow-up check'],
         when=[('Prevent unwanted litters', 'Neutering and spaying are the most reliable way to prevent pregnancy.'),
               ('Health and behaviour', 'Can reduce some health risks and roaming or marking behaviour.'),
               ('Adopted or rescued pets', 'Often recommended soon after adoption.')],
         steps=[('Talk to your vet', 'Discuss timing, benefits and any concerns.'),
                ('Procedure day', 'Fasting, drop-off and a monitored procedure.'),
                ('Rest and recovery', 'A few quiet days at home and a check-up afterwards.')],
         faqs=[('What is the best age?', 'It depends on species, breed and size. Your vet will advise the best time for your pet.'),
               ('Will it change my pet’s personality?', 'Your pet will still be the same animal. It may become calmer and less likely to roam or mark territory, but every pet is different.'),
               ('How long until my pet is back to normal?', 'Most pets are active again within a few days, but strict rest and keeping the wound clean for the time your vet advises is important.')]),
    dict(slug='dentistry', name='Dentistry', group=1, icon='tooth',
         tagline='Healthy teeth and gums, a fresher breath and a happier pet.',
         intro='Dental disease is one of the most common health problems in pets, and it can cause pain and affect the heart and kidneys. Regular dental care keeps teeth and gums healthy and helps your pet eat comfortably.',
         includes=['Oral examination',
                   'Scaling and polishing under anaesthesia',
                   'Treatment of dental problems, including extractions where needed',
                   'Pain relief',
                   'Home dental-care advice for between visits'],
         when=[('Bad breath', 'It is often the first sign of dental disease.'),
               ('Difficulty eating', 'Dropping food, chewing on one side or avoiding hard food.'),
               ('Red or bleeding gums', 'Or visible tartar on the teeth.')],
         steps=[('Oral exam', 'Your vet checks teeth and gums and recommends treatment.'),
                ('Dental treatment', 'Cleaning, polishing and any extractions, under anaesthesia.'),
                ('Home care', 'Tips for brushing and chews to keep teeth healthy.')],
         faqs=[('Why does my pet need anaesthesia for a dental clean?', 'It lets us clean thoroughly, including under the gum line, and examine the whole mouth without stress or pain. It also protects the airway from water and debris.'),
               ('How can I look after my pet’s teeth at home?', 'Daily tooth brushing with pet toothpaste is best. Ask us to show you how, and about suitable dental chews and diets.'),
               ('Will my pet be in pain afterwards?', 'We give pain relief during and after treatment. Most pets eat well the same or next day.')]),
    dict(slug='exotic-animals', name='Exotic Animals', group=1, icon='paw',
         tagline='Care for birds, rabbits and other small companion animals.',
         intro='Birds, rabbits, hamsters, guinea pigs and other small pets have their own special needs. We offer check-ups and care for these companions and give advice on feeding, housing and handling.',
         includes=['Health check for birds, rabbits and small mammals',
                   'Advice on diet, housing and enrichment',
                   'Treatment for common illnesses and injuries',
                   'Nail, beak and teeth care advice',
                   'Guidance for new owners'],
         when=[('New exotic pet', 'Get advice on setting up and feeding your new companion.'),
               ('Changes in behaviour', 'Eating less, hiding, fluffed feathers or a change in droppings.'),
               ('Overgrown nails, beak or teeth', 'These need careful, regular care.')],
         steps=[('Tell us about your pet', 'Species, age, diet and home set-up help us prepare.'),
                ('Gentle examination', 'Handled calmly and carefully for each species.'),
                ('Clear advice', 'Practical guidance to keep your pet healthy at home.')],
         faqs=[('Which animals do you see?', 'We see birds, rabbits and other small companion animals such as hamsters and guinea pigs. Call us before booking if your pet is an unusual species, so we can confirm we can help.'),
               ('How should I bring my exotic pet to the clinic?', 'Use a secure, well-ventilated carrier and keep it warm and covered during travel. Bring a photo of the cage and a sample of the diet if you can.'),
               ('Are exotic pets hard to look after?', 'Each species has specific needs for food, temperature, space and company. We are happy to guide you.')]),

    dict(slug='laboratory', name='Laboratory', group=2, icon='flask',
         tagline='Blood and other tests that show what is happening inside.',
         intro='Laboratory tests give your vet a clear picture of your pet’s health, often before signs of illness are visible. They help us diagnose problems, choose the right treatment and check that it is working.',
         includes=['Blood tests to check organs, blood cells and more',
                   'Urine and stool tests',
                   'Pre-anaesthetic screening',
                   'Monitoring for long-term conditions',
                   'Clear explanation of results'],
         when=[('Before surgery', 'To check your pet is fit for anaesthesia.'),
               ('Unwell pet', 'To help find the cause of illness.'),
               ('Senior check-ups', 'Older pets benefit from regular screening.')],
         steps=[('Sample', 'A quick blood, urine or stool sample.'),
                ('Testing', 'Your sample is tested and reviewed by your vet.'),
                ('Results explained', 'Your vet talks you through what they mean for your pet.')],
         faqs=[('Does my pet need to fast?', 'For some tests, yes. We will tell you at booking whether to withhold food beforehand.'),
               ('How long do results take?', 'It depends on the test. Your vet will tell you when to expect them when the sample is taken.'),
               ('Will my pet need to be sedated?', 'Most pets do not. A small sample is usually quick and easy with gentle handling.')]),
    dict(slug='digital-x-rays', name='Digital X-rays', group=2, icon='scan',
         tagline='Clear images to find the cause of limping, coughing and more.',
         intro='X-rays let your vet see bones, joints, the chest and the abdomen without surgery. Digital images are clear and can be reviewed straight away, helping us reach a diagnosis and plan treatment.',
         includes=['Digital X-ray images of bones, chest and abdomen',
                   'Positioning with care to keep your pet comfortable',
                   'Review of the images by your vet',
                   'Explanation of what the images show',
                   'Copies of images when you need them'],
         when=[('Limping or injury', 'To check for fractures or joint problems.'),
               ('Coughing or breathing difficulty', 'To look at the heart and lungs.'),
               ('Swallowed objects or tummy problems', 'To look for blockages.')],
         steps=[('Examination', 'Your vet decides whether an X-ray will help.'),
                ('Imaging', 'Your pet is positioned gently. Sedation is used only if needed.'),
                ('Results', 'Your vet reviews the images with you and recommends next steps.')],
         faqs=[('Is it safe?', 'X-rays use a small dose of radiation, and our team follows safety procedures. The benefit of a diagnosis is almost always much greater than the small risk.'),
               ('Will my pet need sedation?', 'Some pets lie still, others need light sedation to get a clear picture and stay comfortable. Your vet will decide.'),
               ('Can I stay with my pet?', 'For safety, owners usually wait outside during the X-ray itself, but we will keep you updated.')]),
    dict(slug='ultrasound', name='Ultrasound', group=2, icon='pulse',
         tagline='A gentle, painless look inside the body.',
         intro='Ultrasound uses sound waves to create live pictures of the organs, such as the liver, kidneys, bladder and womb. It is non-invasive and helps your vet find problems that X-rays can miss.',
         includes=['Abdominal ultrasound',
                   'Pregnancy checks',
                   'Examination of organs such as liver, kidneys, bladder and spleen',
                   'Guided sampling when needed',
                   'Explanation of the findings'],
         when=[('Tummy or urinary problems', 'Vomiting, diarrhoea, weight loss or blood in urine.'),
               ('Abnormal blood tests', 'To look at the organs more closely.'),
               ('Pregnancy', 'To confirm and monitor a pregnancy.')],
         steps=[('Preparation', 'Your vet may ask you to withhold food for a few hours.'),
                ('Scan', 'A small area of fur may be clipped. The scan is painless.'),
                ('Findings', 'Your vet explains what they see and recommends next steps.')],
         faqs=[('Does it hurt?', 'No. Ultrasound is painless. Most pets lie calmly while the scan is done.'),
               ('Will my pet’s fur be shaved?', 'A small patch is usually clipped so the images are clear. It grows back.'),
               ('How should I prepare?', 'Your vet will tell you at booking whether to withhold food and whether your pet should have a full bladder.')]),
    dict(slug='mri-ct-scan', name='MRI & CT Scan', group=2, icon='scan',
         tagline='Advanced imaging for the brain, spine and complex problems.',
         intro='MRI and CT scans give very detailed pictures of the brain, spine, joints and other complex areas. When your vet thinks advanced imaging will help, they will explain why, what it involves and what to expect.',
         includes=['Referral and planning by your vet',
                   'Detailed imaging of the brain, spine, joints or body',
                   'Anaesthesia, which is usually needed to keep pets still',
                   'Review of the images by a specialist where needed',
                   'A clear explanation and treatment plan'],
         when=[('Neurological signs', 'Seizures, wobbliness, weakness or balance problems.'),
               ('Back or neck pain', 'To look for spinal disc or nerve problems.'),
               ('Complex cases', 'When X-rays and ultrasound do not give the full answer.')],
         steps=[('Consultation', 'Your vet decides whether advanced imaging is right for your pet.'),
                ('Scan', 'Usually under anaesthesia so your pet is still and comfortable.'),
                ('Results and plan', 'Your vet explains the findings and next steps.')],
         faqs=[('Is a general anaesthetic needed?', 'Usually yes, because the pet must stay completely still for good images. Your vet will check your pet beforehand and monitor throughout.'),
               ('What is the difference between MRI and CT?', 'CT is quick and shows bone and the chest well. MRI shows soft tissue such as the brain and spinal cord in more detail. Your vet will choose the right one.'),
               ('Will my pet stay overnight?', 'It depends on the case. Your vet will tell you what to expect when the scan is planned.')]),
    dict(slug='ecg-eco', name='ECG & ECO', group=2, icon='heart',
         tagline='Heart tests to protect your pet’s most important organ.',
         intro='An ECG records your pet’s heart rhythm, and an echocardiogram (ECO) is an ultrasound of the heart itself. Together they show how well the heart is working and help your vet diagnose and manage heart disease.',
         includes=['ECG to check heart rhythm',
                   'Echocardiogram (heart ultrasound)',
                   'Blood pressure check where needed',
                   'Review by your vet, and referral if needed',
                   'A treatment and monitoring plan'],
         when=[('Heart murmur', 'Found during a routine examination.'),
               ('Coughing, tiredness or fainting', 'Or breathing that is faster than usual.'),
               ('Before anaesthesia', 'For pets with a known or suspected heart condition.')],
         steps=[('Examination', 'Your vet listens to the heart and recommends tests.'),
                ('ECG and scan', 'Painless tests, usually with your pet lying calmly.'),
                ('Plan', 'Your vet explains the results and any treatment.')],
         faqs=[('Are these tests painful?', 'No. An ECG uses small clips on the skin and an echocardiogram is an ultrasound scan, both painless.'),
               ('Does my pet need to be sedated?', 'Most pets are calm enough without sedation. Your vet will decide.'),
               ('How often will tests need to be repeated?', 'It depends on the heart condition. Your vet will tell you if and when to recheck.')]),

    dict(slug='diet-management', name='Diet Management', group=3, icon='leaf',
         tagline='The right food, in the right amount, for your pet.',
         intro='Good nutrition keeps pets healthy at every age. Whether your pet needs to lose weight, has a food allergy, or is entering their senior years, we create a feeding plan that works for them and for you.',
         includes=['Weight and body condition assessment',
                   'A personalised feeding plan',
                   'Weight-loss and weight-gain programmes',
                   'Advice for pets with allergies, kidney, digestive or other health conditions',
                   'Follow-up weigh-ins to check progress'],
         when=[('Overweight or underweight', 'Healthy weight helps pets live longer, happier lives.'),
               ('Food allergies or sensitive tummy', 'Itching, ear problems, vomiting or loose stools.'),
               ('Life-stage changes', 'Puppy, kitten, adult or senior diets.')],
         steps=[('Assessment', 'We weigh your pet and ask about their current food and treats.'),
                ('Feeding plan', 'A plan with the type, amount and schedule of food.'),
                ('Check progress', 'Regular weigh-ins and changes to the plan as needed.')],
         faqs=[('How do I know if my pet is overweight?', 'You should be able to feel the ribs easily under a thin layer of fat and see a waist from above. If you are not sure, we will check at a visit.'),
               ('Can I switch my pet’s food myself?', 'Yes, but change it gradually over a week or so to avoid tummy upsets. Ask us first if your pet has a health condition.'),
               ('Do you recommend special diets?', 'When a health condition needs it, your vet may recommend a specific diet. Otherwise we will help you choose a good everyday food.')]),
    dict(slug='pet-food', name='Pet Food', group=3, icon='bowl',
         tagline='Good food and vet advice, in one place.',
         intro='Choosing the right food can feel overwhelming. We can recommend foods for your pet’s age, size and health, and you can ask about the food and nutrition products we have available at the clinic.',
         includes=['Food recommendations for puppies, kittens, adults and seniors',
                   'Dry and wet food options',
                   'Diets for pets with specific health needs, on your vet’s advice',
                   'Advice on feeding amounts',
                   'Ordering through WhatsApp'],
         when=[('New pet', 'Find the right start-up food for your puppy or kitten.'),
               ('Changing food', 'Get advice on switching safely.'),
               ('Special needs', 'Ask which diets may suit a health condition.')],
         steps=[('Tell us about your pet', 'Age, size, activity and any health concerns.'),
                ('Get a recommendation', 'Your vet or our team suggests suitable options.'),
                ('Order on WhatsApp', 'Ask about availability and collect from the clinic.')],
         faqs=[('Can I see what you stock?', 'Our dog and cat product pages show the kinds of products we offer. Ask on WhatsApp for what is currently available.'),
               ('Do you sell prescription diets?', 'Ask us. If your pet needs a special diet, your vet will tell you which one and where to get it.'),
               ('How do I pay and collect?', 'Place your enquiry on WhatsApp and we will confirm stock, price and when you can collect.')],
         extra=[('Dog food & products', 'dog-products.html#food'), ('Cat food & products', 'cat-products.html#food')]),
    dict(slug='grooming', name='Grooming', group=3, icon='scissors',
         tagline='Clean, comfortable and looking great.',
         intro='Regular grooming is about more than looks. It keeps your pet’s skin and coat healthy, helps spot lumps and skin problems early, and keeps them comfortable. We handle every pet gently and patiently.',
         includes=['Bath and blow-dry',
                   'Brushing and de-matting',
                   'Hair trimming',
                   'Nail trimming',
                   'Ear cleaning and basic hygiene care'],
         when=[('Regular maintenance', 'Every few weeks for most dogs and some cats.'),
               ('Matted or long coats', 'Prevent painful tangles and skin problems.'),
               ('Before an event', 'Look and smell your best.')],
         steps=[('Book a slot', 'Tell us your pet’s breed, size and coat type.'),
                ('Gentle grooming', 'Handled calmly, with breaks for nervous pets.'),
                ('Pick-up', 'A clean, comfortable pet, and tips for coat care at home.')],
         faqs=[('How often should my pet be groomed?', 'It depends on coat type and lifestyle. Short-coated pets may need only occasional baths, while long-coated pets benefit from regular grooming.'),
               ('My pet gets nervous. Can you help?', 'Yes. Tell us beforehand and we will go slowly and take breaks. Some pets prefer a quieter time of day.'),
               ('Do my pet’s vaccinations need to be up to date?', 'It helps protect all the animals at the clinic. Please bring your pet’s vaccination record or ask us what is needed.')]),
]


def icon(name, cls='icon'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def wa(text):
    return f'https://wa.me/{WHATSAPP}?text={quote(text)}'


def page_name(slug):
    return f'service-{slug}.html'


def shared_parts():
    """Header, footer and WhatsApp button from index.html, with in-page links sent back home."""
    src = (ROOT / 'index.html').read_text()
    header = src[src.index('  <header class="header"'):src.index('  </header>') + len('  </header>')]
    tail = src[src.index('  <!-- ============ FOOTER ============ -->'):src.index('</body>')]

    def home_links(part):
        part = re.sub(r'href="#book" ([^>]*)data-service="([^"]+)"',
                      lambda m: f'href="index.html?service={quote(html.unescape(m.group(2)))}#book" {m.group(1)}data-service="{m.group(2)}"',
                      part)
        part = part.replace('href="#home"', 'href="index.html"')
        return re.sub(r'href="#([\w-]+)"', r'href="index.html#\1"', part)

    header = home_links(header).replace(' class="is-active">Home<', '>Home<')
    header = header.replace('class="nav__link" aria-haspopup="true">Services', 'class="nav__link is-active" aria-haspopup="true">Services')
    return header, home_links(tail)


def build(svc):
    name, slug = svc['name'], svc['slug']
    ename = html.escape(name)
    phrase = html.escape(name if re.search(r'[A-Z]{2}', name.replace('X-rays', '')) else name.lower())  # keeps MRI, CT, ECG in capitals
    header, tail = shared_parts()
    book = f"index.html?service={quote(name)}#book"
    group = GROUPS[svc['group']]

    includes = '\n'.join(f'            <li><span class="check" aria-hidden="true">{icon("paw")}</span>{html.escape(t)}</li>' for t in svc['includes'])
    when_icons = ['calendar', 'paw', 'alert']
    when = '\n'.join(f'''          <article class="card reveal">
            <span class="card__icon">{icon(when_icons[i])}</span>
            <h3>{html.escape(t)}</h3>
            <p>{html.escape(d)}</p>
          </article>''' for i, (t, d) in enumerate(svc['when']))
    steps = '\n'.join(f'''          <li class="sv-step reveal">
            <span class="sv-step__num">{i + 1}</span>
            <h3>{html.escape(t)}</h3>
            <p>{html.escape(d)}</p>
          </li>''' for i, (t, d) in enumerate(svc['steps']))
    faqs = '\n'.join(f'''            <details{' open' if i == 0 else ''}>
              <summary><span class="check" aria-hidden="true">{icon("paw")}</span>{html.escape(q)}</summary>
              <p>{html.escape(a)}</p>
            </details>''' for i, (q, a) in enumerate(svc['faqs']))

    related = [s for s in SERVICES if s['group'] == svc['group'] and s['slug'] != slug]
    if len(related) < 3:
        related += [s for s in SERVICES if s['group'] != svc['group']][:3 - len(related)]
    related_cards = '\n'.join(f'''          <article class="card reveal">
            <span class="card__icon">{icon(r['icon'])}</span>
            <h3>{html.escape(r['name'])}</h3>
            <p>{html.escape(r['tagline'])}</p>
            <a href="{page_name(r['slug'])}" class="card__link">Learn more <span aria-hidden="true">&rarr;</span></a>
          </article>''' for r in related[:3])

    extra = ''
    if svc.get('extra'):
        extra = '\n'.join(f'            <a href="{h}" class="sv-extra">{html.escape(t)} <span aria-hidden="true">&rarr;</span></a>' for t, h in svc['extra'])
        extra = f'\n          <div class="sv-extras">\n{extra}\n          </div>'

    doc = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{ename} | Vetriva Animal Hospital, Islamabad</title>
  <meta name="description" content="{html.escape(svc['tagline'])} {ename} at Vetriva Animal Hospital in Islamabad.">
  <meta name="theme-color" content="#0E2944">
  <link rel="icon" type="image/png" href="assets/img/favicon.png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Kaushan+Script&family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
  <script>document.documentElement.classList.add('js');</script>
</head>
<body class="page-service">
  <!-- Generated by tools/build_service_pages.py; edit that script (or index.html for the header/footer) and re-run it. -->

{header}

  <main>
    <section class="page-hero sv-hero texture">
      <div class="sv-cover" aria-hidden="true">
        <img src="assets/img/services/{slug}.webp" alt="" style="object-position: {FOCUS[slug]}" fetchpriority="high">
        <span class="sv-badge">{icon(svc['icon'])}</span>
      </div>
      <div class="container page-hero__grid">
        <div class="page-hero__copy">
          <nav class="crumbs" aria-label="Breadcrumb">
            <a href="index.html">Home</a><span aria-hidden="true">/</span><a href="index.html#services">Services</a><span aria-hidden="true">/</span><span aria-current="page">{ename}</span>
          </nav>
          <p class="sv-group">{html.escape(group)}</p>
          <h1>{ename}</h1>
          <p class="page-hero__lead">{html.escape(svc['tagline'])}</p>
          <div class="page-hero__actions">
            <a href="{book}" class="btn btn--light">Book this service</a>
            <a href="{wa(f'Hello Vetriva, I would like to ask about {name.lower()}.')}" class="page-hero__switch" target="_blank" rel="noopener">Ask on WhatsApp <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
      </div>
      <svg class="wave wave--bottom" viewBox="0 0 1440 200" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0 150c180-10 330 40 520 36 230-5 330-90 560-120 140-18 250-6 360 10v124H0Z"/>
      </svg>
    </section>

    <section class="section sv-about">
      <div class="container sv-about__grid">
        <div class="sv-about__copy reveal">
          <p class="label">About this service</p>
          <h2>What is {phrase}?</h2>
          <p>{html.escape(svc['intro'])}</p>{extra}
        </div>
        <div class="sv-included reveal">
          <h3>What is included</h3>
          <ul>
{includes}
          </ul>
          <a href="{book}" class="btn btn--primary">Book now</a>
        </div>
      </div>
    </section>

    <section class="section sv-tint">
      <div class="container">
        <div class="section__head reveal">
          <h2>When to book</h2>
          <p>Common reasons to come in for {phrase}.</p>
        </div>
        <div class="cards cards--3">
{when}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section__head reveal">
          <h2>How it works</h2>
          <p>Simple from start to finish.</p>
        </div>
        <ol class="sv-steps">
{steps}
        </ol>
      </div>
    </section>

    <section class="section sv-tint">
      <div class="container sv-faq">
        <div class="section__head section__head--left reveal">
          <p class="label">FAQ</p>
          <h2>Questions about {phrase}</h2>
          <p>Can&rsquo;t find your answer? <a href="index.html#contact">Get in touch</a> and we&rsquo;ll be happy to help.</p>
        </div>
        <div class="accordion reveal" id="accordion">
{faqs}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section__head reveal">
          <h2>Related services</h2>
          <p>Other ways we can care for your pet.</p>
        </div>
        <div class="cards cards--3">
{related_cards}
        </div>
      </div>
    </section>

    <section class="pcta">
      <div class="container">
        <div class="pcta__box reveal">
          <div>
            <h2>Ready to book {ename}?</h2>
            <p>Choose a time that suits you, or message us on WhatsApp with any questions.</p>
          </div>
          <div class="pcta__actions">
            <a href="{book}" class="btn btn--light">Book appointment</a>
            <a href="{wa(f'Hello Vetriva, I would like to book {name.lower()}.')}" class="pcta__wa" target="_blank" rel="noopener">Ask on WhatsApp <span aria-hidden="true">&rarr;</span></a>
          </div>
        </div>
      </div>
    </section>
  </main>

{tail}</body>
</html>
'''
    (ROOT / page_name(slug)).write_text(doc)


if __name__ == '__main__':
    for s in SERVICES:
        build(s)
    print(f'wrote {len(SERVICES)} service pages')
