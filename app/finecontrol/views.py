# IMPORTS FOR CLASS BASED View
from connection.forms import OC_LAB
from connection.models import Connection_Db
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.core import serializers
from .forms import CleaningProcessForm, ZeroPosition_Form
from .models import *
from printrun import printcore, gcoder
import time
import os

form ={}

CLEANINGPROCESS_INITIALS = {'start_frequency':100,
                            'stop_frequency':500,
                            'steps':50,
                            'pressure':20}


class SyringeLoad(View):
    # def post:
    def get(self, request):
        if "LISTLOAD" in request.GET:
            syringe_load_db = SyringeLoad_Db.objects.filter(author=request.user).order_by('volume')
            volumes = [i.volume for i in syringe_load_db]
            return JsonResponse(volumes, safe=False)

    def post(self, request):
        # Creates a new vol in the database
        if 'SAVEMOVEMOTOR' in request.POST:
            try:
                SyringeLoad_Db.objects.filter(volume=request.POST['SAVEMOVEMOTOR']).filter(author=request.user)[0]
                return JsonResponse("Volume already exist!", safe=False)
            except IndexError:
                syringe_load = SyringeLoad_Db.objects.create(volume=request.POST['SAVEMOVEMOTOR'],
                                                             author=request.user)
                syringe_load.save()
                return JsonResponse("Volume saved!", safe=False)

        if 'DELETE' in request.POST:
            try:
                SyringeLoad_Db.objects.filter(volume=request.POST['DELETE']).filter(author=request.user)[0].delete()
                return JsonResponse("Volume Deleted!", safe=False)
            except IndexError:
                return JsonResponse("Volume doesn't exist!", safe=False)

        if 'MOVEMOTOR' in request.POST:
            mm_movement = round(-56*float(request.POST['MOVEMOTOR'])+58, 2);
            OC_LAB.send(f"G28Z")
            OC_LAB.send(f"G1Z{mm_movement}")
            return JsonResponse("Volume save", safe=False)

    # def delete(self,request):
    #     # Eliminates a vol from the database
    #     print(request)
    #     # if 'MOVEMOTOR' in request:
    #     #     try:
    #     #         SyringeLoad_Db.objects.filter(volume=request.POST['MOVEMOTOR']).filter(author=request.user)[0].delete()
    #     #         return JsonResponse("Volume Deleted!", safe=False)
    #     #     except IndexError:
    #     return JsonResponse("Volume doesn't exist!", safe=False)

    # def options(self, request):
    #     if 'MOVEMOTOR' in request.OPTIONS:
    #         print("Finish It!!")
    #         return JsonResponse("Volume save", safe=False)

""" class HommingSetup(View):
    def post(self, request):
        if request.POST.get('setzero'):
            print(request.POST)
            zeros_values = list(request.POST['setzero'].split(","))
            zero_on_DB = ZeroPosition(uploader=request.user,
                                      zero_x=float(zeros_values[0]),
                                      zero_y=float(zeros_values[1]))
            zero_on_DB.save()
            OC_LAB.send(f'G92X0Y0')
            return JsonResponse({'message': 'ok'})

    def get(self, request):
        if 'getzero' in request.GET:
            last_zero_position = ZeroPosition.objects.filter(uploader=request.user).order_by('-id')[0]
            OC_LAB.send(f'G0X{last_zero_position.zero_x}Y{last_zero_position.zero_y}\nG92X0Y0')
        return JsonResponse({'message':'ok'}) """


class Cleaning(object):

    def __init__(self):
        self.time_window = 1  # Minimun time for each frequency 5 sec
        self.duration = 0
        self.lines_left = 0

    def dinamic_cleaning(self, fi, fo, step, pressure):
        # THE GCODE TO OPEN THE VALVE AT A CERTAIN frequency
        # range(start, stop, step)
        self.duration = 0
        dinamic_clean = []
        for i in range(fi, fo + step, step):
            for j in range(1, self.time_window * i + 1):
                dinamic_clean.append(f'G97 P{pressure}' + '\n')
                dinamic_clean.append(f'G98 F{i}' + '\n')
                self.lines_left += 1
            self.duration += self.time_window

        return dinamic_clean

    def static_cleaning(self, volume):
        # Gcode to move the Pump for a specific volume from 0-position
        zMovement = round(volume * 57 / 1000, 2)

        gcode = ['G91', f'G1Z{zMovement}', 'G90']
        return gcode


clean = Cleaning()


class MotorControl(View):
    # Manage the GET request
    def get(self, request):
        return render(
            request,
            "./motorcontrol.html",
            form)


class Clean(View):
    CLEANINGPROCESS_INITIALS = {'start_frequency': 100,
                                'stop_frequency': 500,
                                'steps': 50,
                                'pressure': 15}

    def get(self, request):
        OC_LAB.send('G28XY')
        form['CleaningProcessForm'] = CleaningProcessForm(initial=CLEANINGPROCESS_INITIALS)
        return render(
            request,
            "./cleanprocess.html",
            form)

    def post(self, request):
        if 'cycles' in request.POST:
            for i in range(0, int(request.POST['cycles'])):
                OC_LAB.send('M42 P63 T')
        return render(
            request,
            "./cleanprocess.html",
            {**form})


clean = Cleaning();


class StaticPurge(View):
    def post(self, request):
        if request.POST.get('cycles'):
            gcode = clean.static_cleaning(int(request.POST.get('cycles')))
            light_gcode = gcoder.LightGCode(gcode)
            OC_LAB.startprint(light_gcode)
        return JsonResponse({'message': 'ok'})

    def get(self, request):
        return JsonResponse({'message': 'ok'})


class CleanControl(View):
    def post(self, request):
        if 'PROCESS' in request.POST:
            clean_param = CleaningProcessForm(request.POST)

            if clean_param.is_valid():
                clean_param = clean_param.cleaned_data
                gcode = clean.dinamic_cleaning(clean_param['start_frequency'],
                                               clean_param['stop_frequency'],
                                               clean_param['steps'],
                                               clean_param['pressure'])
                light_gcode = gcoder.LightGCode(gcode)
                OC_LAB.startprint(light_gcode)

                data = {'message': f'Cleaning process in progress, please wait! \n'}
                data.update({'duration': clean.duration})
            else:
                data = {'message': 'ERROR'}
                print(clean_param.errors)
            return JsonResponse(data)

        if 'STOP' in request.POST:
            OC_LAB.cancelprint()
            return JsonResponse({'message': 'stopped'})
        if 'PAUSE' in request.POST:
            OC_LAB.pause()
            return JsonResponse({'message': 'paused'})

    def get(self, request):
        # Check the status
        if 'checkstatus' in request.GET:
            data = {'busy': 'true',
                    'message': '',
                    }
            if OC_LAB.printing:
                data['message'] = f'Cleaning process in progress, please wait! \n'
                return JsonResponse(data)
            else:
                data['busy'] = 'false'
                data['message'] = 'Done!'
                return JsonResponse(data)


class GcodeEditor(View):

    def get(self, request):
        form['list_load'] = GcodeFile.objects.filter(uploader=request.user).order_by('-id')

        # LIST LOADING
        if 'LISTLOAD' in request.GET:
            gcodefiles = GcodeFile.objects.filter(uploader=request.user).order_by('-id')
            names = [i.filename for i in gcodefiles]
            return JsonResponse(names, safe=False)

        # FILE LOADING
        if 'LOADFILE' in request.GET:
            filename = request.GET.get('filename')
            gcodefile = GcodeFile.objects.filter(uploader=request.user, filename=filename)

            # Open the file
            with open(str(gcodefile[0].gcode), 'r') as f:
                text = f.read()

            response = {'text': text,
                        'filename': gcodefile[0].filename,
                        'success': 'File opened!'}
            return JsonResponse(response)

        return render(
            request,
            "./gcodeeditor.html",
            form)


    def post(self, request):
        # print(request.POST)
        if 'UPLOAD' in request.POST:
            if request.FILES['file']:
                uploaded_file = request.FILES['file']

                if GcodeFile.objects.filter(filename=uploaded_file, uploader=request.user):
                    return JsonResponse({'danger': 'Filename already exist, change it!'})

                if 'gcode' in uploaded_file.content_type:
                    fs = FileSystemStorage('media/gfiles/')
                    new_name = fs.save(uploaded_file.name, uploaded_file)

                    gcode = GcodeFile()
                    gcode.filename = uploaded_file.name;
                    gcode.gcode = fs.location + '/' + new_name;
                    gcode.gcode_url = fs.url(new_name)
                    gcode.uploader = request.user
                    gcode.save()
                    return JsonResponse({'success': 'File Saved!'})
                else:
                    print('entro al else')
                    return JsonResponse({'danger': 'Invalid File'})
            else:
                return JsonResponse({'danger': 'Please select a File'})

        # SAVE FILE
        if 'SAVE' in request.POST:

            filename = request.POST.get('name')
            text = request.POST.get('text')
            fs = FileSystemStorage('media/gfiles/')
            gcodefile = GcodeFile.objects.filter(uploader=request.user, filename=filename)

            # if the file exist then edit
            if gcodefile:
                # Get realitve path from app folder so that can be opened
                path_rel = os.path.relpath(str(gcodefile[0].gcode), '/app/')
                with open(path_rel, 'w+') as f:
                    myfile = File(f)
                    myfile.write(text)
                    new_name = fs.save(filename + '.gcode', content=myfile)
                return JsonResponse({'info': f'{filename} edited'})

            # Create the file
            with open(f'last.gcode', 'w+') as f:
                myfile = File(f)
                myfile.write(text)
                new_name = fs.save(filename + '.gcode', content=myfile)

                gcode = GcodeFile()
                gcode.filename = filename;
                gcode.gcode = fs.location + '/' + new_name;
                gcode.gcode_url = fs.url(new_name)
                gcode.uploader = request.user
                gcode.save()
                return JsonResponse({'success': 'File Saved!'})

        # REMOVE FILE
        if 'REMOVE' in request.POST:
            filename = request.POST.get('name')
            if not filename:
                return JsonResponse({'warning': 'Choose a file!'})

            try:
                file = GcodeFile.objects.get(filename=filename, uploader=request.user)
                file.delete()
            except:
                return JsonResponse({'warning': 'Something went wrong!'})

            return JsonResponse({'success': 'File removed!'})

        # RUN FILE
        if 'START' in request.POST:
            filename = request.POST.get('name')
            if not filename:
                return JsonResponse({'warning': 'First save the file and Open it!'})
            try:
                file = GcodeFile.objects.get(filename=filename, uploader=request.user)
                if file:
                    with open(f'{file.gcode}', 'r') as f:
                        lines_gcode = [code_line.strip() for code_line in f]
                        light_gcode = gcoder.LightGCode(lines_gcode)
                        OC_LAB.startprint(light_gcode)
                        return JsonResponse({'success': 'Printing!'})
            except DoesNotExist:
                return JsonResponse({'danger': 'File Not Found'})

        # STOP FILE
        if 'STOP' in request.POST:
            OC_LAB.cancelprint()
            return JsonResponse({'danger': 'STOP'})
