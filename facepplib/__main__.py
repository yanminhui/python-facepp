"""
Provides FacePP Demo.
"""

from __future__ import print_function, unicode_literals

import json

from . import FacePP, exceptions


def face_detection(app):
    """
    Detect and analyze human faces within the image that you provided.
    """
    print('[Face Detection]')

    img_url = 'https://www.faceplusplus.com/scripts/demoScript/images/demo-pic6.jpg'
    img = app.image.get(image_url=img_url,
                        return_attributes=['age'])

    print('image', '=', img)
    print('faces_count', '=', len(img.faces))

    for (idx, face_) in enumerate(img.faces):
        print('-', ''.join(['[', str(idx), ']']))
        print('face', '=', face_)
        print('gender', '=', face_.gender['value'])
        print('age', '=', face_.age['value'])
        print('face_rectangle', '=', json.dumps(face_.face_rectangle, indent=4))


def face_comparing(app):
    """
    Compare two faces and decide whether they are from the same person.
    """
    print('[Face Comparing]')

    img_url1 = 'https://www.faceplusplus.com/scripts/demoScript/images/demo-pic32.jpg'
    img_url2 = 'https://www.faceplusplus.com/scripts/demoScript/images/demo-pic22.jpg'
    cmp_ = app.compare.get(image_url1=img_url1,
                           image_url2=img_url2)

    print('image1', '=', cmp_.image1)
    print('image2', '=', cmp_.image2)

    print('thresholds', '=', json.dumps(cmp_.thresholds, indent=4))
    print('confidence', '=', cmp_.confidence)


def faceset_initialize(app):
    """
    Initialize FaceSet and set `python-facepp` for outer_id.
    """
    print('[FaceSet Initialize]')

    # Create FaceSet
    group_id = 'python-facepp'
    faceset_ = None
    for item in app.face_set.all():
        if item.outer_id == group_id:
            faceset_ = item
        else:
            print('~ FaceSet:', repr(item))
        # Delete FaceSet
        # app.face_set.delete(faceset_token=item.internal_id, check_empty=0)

    if faceset_ is None:
        faceset_ = app.face_set.create(outer_id=group_id,
                                       display_name='Python-FacePP')
        print('-', 'Create FaceSet:', faceset_)
    else:
        print('-', 'Found FaceSet:', faceset_)

    # Add Face
    imgs = {
        'Old Man': 'https://www.faceplusplus.com/images/comparing/left_pic_one.jpg',
        'Woman': 'https://www.faceplusplus.com/images/comparing/left_pic_two.jpg',
        'Man': 'https://www.faceplusplus.com/images/comparing/left_pic_three.jpg',
        'Young Girl': 'https://www.faceplusplus.com/images/comparing/left_pic_four.jpg',
        'Girl': 'https://www.faceplusplus.com/images/comparing/left_pic_five.jpg'
    }

    print('-', 'Add Face')
    for img_name in imgs:
        for face_ in app.face.all(image_url=imgs[img_name]):
            # Set `user_id` to face and add face to face_set.
            face_.save(outer_ids=[group_id], user_id=img_name)
            print('-', '-', ': '.join([img_name, face_.internal_id]))

    # FaceSet Information
    print('-', 'FaceSet Information')
    faceset_ = app.face_set.get(outer_id=group_id)
    print('-', '-', 'Outer ID:', faceset_.outer_id)
    print('-', '-', 'Display Name:', faceset_.display_name)
    print('-', '-', 'Face Count:', faceset_.face_count)


def face_search(app):
    """
    Find one or more most similar faces from Faceset, to a new face.
    """
    print('[Face Search]')

    img_url = 'https://www.faceplusplus.com.cn/images/comparing/left_pic_four.jpg'
    group_id = 'python-facepp'
    search_ = app.search.get(image_url=img_url,
                             outer_id=group_id)

    print('image', '=', search_.image)
    print('thresholds', '=', json.dumps(search_.thresholds, indent=4))

    for (idx, face_) in enumerate(search_.results):
        print('-', ''.join(['[', str(idx), ']']), face_.user_id)
        print('gender', '=', face_.gender['value'])
        print('age', '=', face_.age['value'])
        print('confidence', '=', face_.confidence)


def face_landmarks(app):
    """
    Locate and return keypoints of face components, including face contour, eye, eyebrow, lip and nose contour.
    """
    print('[Face Landmarks]')

    img_url = 'https://www.faceplusplus.com/scripts/demoScript/images/demo-pic6.jpg'
    img = app.image.get(image_url=img_url)

    print('image', '=', img)
    print('faces_count', '=', len(img.faces))

    for idx, face_ in enumerate(app.face.filter(face_tokens=[item.internal_id for item in img.faces],
                                                return_landmark=1)):
        print('-', ''.join(['[', str(idx), ']']))
        print('face', '=', face_)
        print('landmark', '=', json.dumps(face_.landmark, indent=4))


def dense_facial_landmarks(app):
    """
    Accurately locate facial features and facial contours. Return 1000 facial key points.
    """
    print('[Dense Facial Landmarks]')

    img_url = 'https://www.faceplusplus.com/scripts/demoScript/images/demo-pic30.jpg'

    print('image', '=', img_url)
    for idx, face_ in enumerate(app.face.filter(image_url=img_url,
                                                return_landmark='all')):
        print('-', ''.join(['[', str(idx), ']']))
        print('face', '=', face_)
        print('landmark', '=', json.dumps(face_.landmark, indent=4))


def face_attributes(app):
    """
    Analyze a series of face related attributes including age, gender,
    smile intensity, head pose, eye status, emotion, beauty, eye gaze,
    mouth status, skin status, ethnicity, face image quality and blurriness.
    """
    print('[Face Attributes]')

    img_url = 'https://www.faceplusplus.com.cn/scripts/demoScript/images/demo-pic6.jpg'
    img = app.image.get(image_url=img_url)

    print('image', '=', img)
    print('faces_count', '=', len(img.faces))

    for idx, face_ in enumerate(app.face.filter(face_tokens=[item.internal_id for item in img.faces],
                                                return_attributes=['age', 'gender', 'smiling'])):
        print('-', ''.join(['[', str(idx), ']']))
        print('face', '=', face_)
        print('age', '=', face_.age['value'])
        print('gender', '=', face_.gender['value'])
        print('smile', '=', face_.smile['value'])  # warning: `return_attributes` is required.
        print('beauty', '=', json.dumps(face_.beauty))
        print('face_rectangle', '=', json.dumps(face_.face_rectangle))


def beauty_score_and_emotion_recognition(app):
    """
    Compute beauty scores for detected faces from both male's and female's perspective.
    """
    print('[Beauty Score | Emotion Recognition]')

    img_url = 'https://www.faceplusplus.com/scripts/demoScript/images/demo-pic105.jpg'
    img = app.image.get(image_url=img_url)

    print('image', '=', img)
    print('faces_count', '=', len(img.faces))

    for idx, face_ in enumerate(img.faces):
        print('-', ''.join(['[', str(idx), ']']))
        print('face', '=', face_)

        print('Beauty Score:')
        for k, v in face_.beauty.items():
            print(' ', k, '=', v)

        print('Emotion Recognition:')
        for k, v in face_.emotion.items():
            print(' ', k, '=', v)


if __name__ == '__main__':

    api_key = 'eFWami68yL25RPrSuG0oi0lFfYRle26L'
    api_secret = 'Zf_obifstMlZTPmejoY1MHNKyioD_Jtz'

    try:
        app_ = FacePP(api_key=api_key, api_secret=api_secret)

        funcs = [
            face_detection,
            face_comparing,
            faceset_initialize,
            face_search,
            face_landmarks,
            dense_facial_landmarks,
            face_attributes,
            beauty_score_and_emotion_recognition
        ]

        for func in funcs:
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            func(app_)

    except exceptions.BaseFacePPError as e:
        print('Error:', e)

