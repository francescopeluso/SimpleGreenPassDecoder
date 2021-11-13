import sys
import json
import zlib
import cbor2
import emoji
import base45
from PIL import Image
from datetime import datetime
from pyzbar.pyzbar import decode
from cose.messages import CoseMessage
from pdf2image import convert_from_path

def print_data(data):
    print()
    print(emoji.emojize(":bust_in_silhouette: This certificate belongs to " + data['-260']['1']['nam']['gn'] + " " + data['-260']['1']['nam']['fn'] + ", born on " + data['-260']['1']['dob'] + "."))
    print(emoji.emojize(":classical_building:  The certificate has been generated by " + data['-260']['1']['v'][0]['is'] + " [" + str(data['1']) + "] on " + datetime.utcfromtimestamp(int(data['6'])).strftime('%Y-%m-%d') + "."))
    print()
    print(emoji.emojize(":identification_card:  Unique Certificate ID: " + data['-260']['1']['v'][0]['ci']))
    print(emoji.emojize(":syringe: Number of doses received: " + str(data['-260']['1']['v'][0]['dn']) + " out of " + str(data['-260']['1']['v'][0]['sd'])))
    print(emoji.emojize(":calendar: Expiration date of the certificate: " + datetime.utcfromtimestamp(int(data['4'])).strftime('%Y-%m-%d')))
    print()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(emoji.emojize('\n:warning:  Usage: python gp_decoder.py <file path>'))
        sys.exit(1)

    print(emoji.emojize('\n:hourglass_done: Decoding the QR code you gave me...'))
    path = sys.argv[1]

    qr_data = None;

    if path.endswith('.pdf'):
        images = convert_from_path(path, dpi=300)
        for image in images:
            qr_data = decode(image)
            if qr_data:
                qr_data = qr_data[0].data.decode('utf-8')
                break
    else:
        image = Image.open(path)
        qr_data = decode(image)
        qr_data = qr_data[0].data.decode('utf-8')

    if qr_data is not None:
        try:
            qr_data = qr_data[4:]
            qr_data = base45.b45decode(qr_data)
            qr_data = zlib.decompress(qr_data)
            qr_data = CoseMessage.decode(qr_data)
            qr_data = json.dumps(cbor2.loads(qr_data.payload), indent = 2)

            # string to json object
            print_data(json.loads(qr_data))

        except Exception as e:
            print('Error: Green Pass QR code is not valid')
            sys.exit(1)

    else:
        print('No QR data found')
        sys.exit(1)