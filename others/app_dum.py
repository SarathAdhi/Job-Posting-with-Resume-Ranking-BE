import random
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
from others.Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos


save_image_path = './resumes/data-scientist-1559725114.pdf'


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(
        resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


def course_recommender(course_list):
    c = 0
    rec_course = []
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        rec_course.append(c_name)

    return rec_course


def run():
    resume_data = ResumeParser(save_image_path).get_extracted_data()
    resume_text = pdf_reader(save_image_path)

    print(resume_data)

    # Candidate Level

    cand_level = ''
    if resume_data['no_of_pages'] == 1:
        cand_level = "Fresher"
    elif resume_data['no_of_pages'] == 2:
        cand_level = "Intermediate"
    elif resume_data['no_of_pages'] >= 3:
        cand_level = "Experienced"

    # recommendation
    ds_keyword = ['tensorflow', 'keras', 'pytorch',
                  'machine learning', 'deep Learning', 'flask', 'streamlit']
    web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                   'javascript', 'angular js', 'c#', 'flask']
    android_keyword = ['android', 'android development',
                       'flutter', 'kotlin', 'xml', 'kivy']
    ios_keyword = ['ios', 'ios development',
                   'swift', 'cocoa', 'cocoa touch', 'xcode']
    uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                    'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']

    recommended_skills = []
    reco_field = ''
    rec_course = ''

    # Courses recommendation
    for i in resume_data['skills']:
        # Data science recommendation
        if i.lower() in ds_keyword:
            print(i.lower())
            reco_field = 'Data Science'
            recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling', 'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                  'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras', 'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask", 'Streamlit']
            rec_course = course_recommender(ds_course)
            break

        # Web development recommendation
        elif i.lower() in web_keyword:
            print(i.lower())
            reco_field = 'Web Development'
            recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel',
                                  'Magento', 'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
            rec_course = course_recommender(web_course)
            break

        # Android App Development
        elif i.lower() in android_keyword:
            print(i.lower())
            reco_field = 'Android Development'
            recommended_skills = ['Android', 'Android development', 'Flutter',
                                  'Kotlin', 'XML', 'Java', 'Kivy', 'GIT', 'SDK', 'SQLite']
            rec_course = course_recommender(android_course)
            break

        # IOS App Development
        elif i.lower() in ios_keyword:
            print(i.lower())
            reco_field = 'IOS Development'
            recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                  'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation', 'Auto-Layout']
            rec_course = course_recommender(ios_course)
            break

        # Ui-UX Recommendation
        elif i.lower() in uiux_keyword:
            print(i.lower())
            reco_field = 'UI-UX Development'
            recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq', 'Prototyping', 'Wireframes', 'Storyframes',
                                  'Adobe Photoshop', 'Editing', 'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe', 'Solid', 'Grasp', 'User Research']
            rec_course = course_recommender(uiux_course)
            break

        resume_score = 0
        if 'Objective' in resume_text:
            resume_score = resume_score+20
            # Awesome! You have added Objective
        else:
            print("According to our recommendation please add your career objective, it will give your career intension to the Recruiters.")
            # According to our recommendation please add your career objective, it will give your career intension to the Recruiters.

        if 'Declaration' in resume_text:
            resume_score = resume_score + 20
            # Awesome! You have added Delcaration✍
        else:
            print("According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you")
            # According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you

        if 'Hobbies' or 'Interests' in resume_text:
            resume_score = resume_score + 20
            # Awesome! You have added your Hobbies⚽
        else:
            print("According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.")
            # According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.

        if 'Achievements' in resume_text:
            resume_score = resume_score + 20
            # Awesome! You have added your Achievements🏅
        else:
            print("According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.")
            # According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.

        if 'Projects' in resume_text:
            resume_score = resume_score + 20
            # Awesome! You have added your Projects 👨‍💻
        else:
            print("According to our recommendation please add Projects 👨‍💻. It will show that you have done work related the required position or not.")
            # According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not.

    print(resume_score)


run()
