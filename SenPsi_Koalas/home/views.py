from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.db.models import Q, Max, Sum, Min, F, Count, ExpressionWrapper, Func, DateTimeField, DateField
from django.db.models.functions import TruncDate, TruncMonth, TruncYear, TruncDay
from datetime import datetime, timedelta
from .models import Calls, Messages, Client
from django.contrib.auth.models import User
from admin_volt_pro.forms import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage


def get_time_type(request, device_id):
    start_time = None
    end_time = None
    time_type = None
    if request.GET.get('start_time') is not None:
        start_time = datetime.strptime(request.GET.get('start_time'), "%Y-%m-%d").timestamp() * 1000
    if request.GET.get('end_time') is not None:
        end_time = datetime.strptime(request.GET.get('end_time'), "%Y-%m-%d").timestamp() * 1000
    if request.GET.get('time_type') is not None:
        time_type = request.GET.get('time_type')

    # if end_time is None and start_time is not None:
    #     end_time = (datetime.fromtimestamp(start_time / 1000) - timedelta(days=14)).timestamp() * 1000
    # elif end_time is None:
    #     end_time = Calls.objects.filter(device_id=device_id).aggregate(Max("timestamp"))["timestamp__max"]
    # if start_time is None:
    #     start_time = (datetime.fromtimestamp(end_time / 1000) - timedelta(days=14)).timestamp() * 1000
    if start_time is None or end_time is None:
        return JsonResponse({'error_message': 'Invalid time range'}, status=400)
    if time_type is None:
        time_type = '0'
    if start_time > end_time:
        return JsonResponse({'error_message': 'Invalid time range'}, status=400)
    return start_time, end_time, time_type


@permission_required("home.view_calls")
def get_call_duration_time(request, id):
    try:
        client = Client.objects.get(client_id=id)
        device_id = client.client_device_id
        if client.client_device_id is None:
            return JsonResponse({'error_message': 'Client Doesn\'t Have Device Id'}, status=404)
    except Client.DoesNotExist:
        return JsonResponse({'error_message': 'No Client'}, status=404)
    time_type_result = get_time_type(request, device_id)
    if isinstance(time_type_result, JsonResponse):
        return time_type_result
    start_time, end_time, time_type = time_type_result
    if time_type not in ['0','1','2']:
        return JsonResponse({'error_message': 'Invalid timetype'}, status=400)
    result = Calls.objects.filter(device_id=device_id, timestamp__range=[start_time, end_time]).exclude(
        call_type=3).annotate(
        date=TruncDay(
            Func(
                F('timestamp') / 1000,
                function='from_unixtime',
                output_field=DateField(),
            ),
        )
    )
    if time_type == '0':
        if (datetime.fromtimestamp(end_time / 1000.0) - datetime.fromtimestamp(start_time / 1000.0)).days + 1 > 14:
            return JsonResponse({'error_message': 'Invalid time range'}, status=400)
        result = result.annotate(
            timestamp_to_date=TruncDay(
                Func(
                    F('timestamp') / 1000,
                    function='from_unixtime',
                    output_field=DateField(),
                ),
            ),
        )
    elif time_type == '1':
        e = datetime.fromtimestamp(end_time / 1000.0)
        s = datetime.fromtimestamp(start_time / 1000.0)
        if (e.year - s.year) * 12 + (e.month - s.month) + 1 > 12:
            return JsonResponse({'error_message': 'Invalid time range'}, status=400)
        result = result.annotate(
            timestamp_to_date=TruncMonth(
                Func(
                    F('timestamp') / 1000,
                    function='from_unixtime',
                    output_field=DateField(),
                ),
            ),
        )
    elif time_type == '2':
        e = datetime.fromtimestamp(end_time / 1000.0)
        s = datetime.fromtimestamp(start_time / 1000.0)
        if e.year - s.year + 1 > 12:
            return JsonResponse({'error_message': 'Invalid time range'}, status=400)
        result = result.annotate(
            timestamp_to_date=TruncYear(
                Func(
                    F('timestamp') / 1000,
                    function='from_unixtime',
                    output_field=DateField(),
                ),
            ),
        )
    record = result.values('call_type', 'timestamp_to_date').annotate(
        total_duration=Sum('call_duration'),
        min_time=Min('date'),
        max_time=Max('date')
    ).order_by('timestamp_to_date')
    context = {'record': list(record)}
    return JsonResponse(context)


@permission_required("home.view_calls")
def get_call_counts_time(request, id):
    try:
        client = Client.objects.get(client_id=id)
        device_id = client.client_device_id
        if client.client_device_id is None:
            return JsonResponse({'error_message': 'Client Doesn\'t Have Device Id'}, status=404)
    except Client.DoesNotExist:
        return JsonResponse({'error_message': 'No Client'}, status=404)
    time_type_result = get_time_type(request, device_id)
    if isinstance(time_type_result, JsonResponse):
        return time_type_result
    start_time, end_time, time_type = time_type_result
    if time_type not in ['0','1','2']:
        return JsonResponse({'error_message': 'Invalid timetype'}, status=400)
    result = Calls.objects.filter(device_id=device_id, timestamp__range=[start_time, end_time]).annotate(
        date=TruncDay(
            Func(
                F('timestamp') / 1000,
                function='from_unixtime',
                output_field=DateField(),
            ),
        )
    )
    if time_type == '0':
        if (datetime.fromtimestamp(end_time / 1000.0) - datetime.fromtimestamp(start_time / 1000.0)).days + 1 > 14:
            return JsonResponse({'error_message': 'Invalid time range'}, status=400)
        result = result.annotate(
            timestamp_to_date=TruncDay(
                Func(
                    F('timestamp') / 1000,
                    function='from_unixtime',
                    output_field=DateField(),
                ),
            ),
        )
    elif time_type == '1':
        e = datetime.fromtimestamp(end_time / 1000.0)
        s = datetime.fromtimestamp(start_time / 1000.0)
        if (e.year - s.year) * 12 + (e.month - s.month) + 1 > 12:
            return JsonResponse({'error_message': 'Invalid time range'}, status=400)
        result = result.annotate(
            timestamp_to_date=TruncMonth(
                Func(
                    F('timestamp') / 1000,
                    function='from_unixtime',
                    output_field=DateField(),
                ),
            ),
        )
    elif time_type == '2':
        e = datetime.fromtimestamp(end_time / 1000.0)
        s = datetime.fromtimestamp(start_time / 1000.0)
        if e.year - s.year + 1 > 12:
            return JsonResponse({'error_message': 'Invalid time range'}, status=400)
        result = result.annotate(
            timestamp_to_date=TruncYear(
                Func(
                    F('timestamp') / 1000,
                    function='from_unixtime',
                    output_field=DateField(),
                ),
            ),
        )
    record = result.values('call_type', 'timestamp_to_date').annotate(
        counts=Count('call_type'),
        min_time=Min('date'),
        max_time=Max('date')
    ).order_by('timestamp_to_date')
    context = {'record': list(record)}
    return JsonResponse(context)


@permission_required("home.view_calls")
def get_call_duration_trace(request, id):
    try:
        client = Client.objects.get(client_id=id)
        device_id = client.client_device_id
        if client.client_device_id is None:
            return JsonResponse({'error_message': 'Client Doesn\'t Have Device Id'}, status=404)
    except Client.DoesNotExist:
        return JsonResponse({'error_message': 'No Client'}, status=404)
    time_type_result = get_time_type(request, device_id)
    # if isinstance(time_type_result, JsonResponse):
    #     return time_type_result
    start_time, end_time, time_type = time_type_result
    # if time_type not in ['0','1','2']:
    #     return JsonResponse({'error_message': 'Invalid timetype'}, status=400)
    call_type = request.GET.get('call_type')
    result = Calls.objects.filter(device_id=device_id, timestamp__range=[start_time, end_time]).exclude(call_type=3)
    if call_type is None:
        top10 = result.values('trace').annotate(
            combined_duration=Sum('call_duration'),
        ).order_by('-combined_duration')[:10]
        top10_trace_list = [i['trace'] for i in top10]
        temp_record = result.values('call_type', 'trace').annotate(
            total_duration=Sum('call_duration'),
        )
        record = temp_record.filter(trace__in=top10_trace_list)
    else:
        if call_type not in ['1','2']:
            return JsonResponse({'error_message': 'Invalid call type'}, status=400)
        record = result.filter(call_type=call_type).values('call_type', 'trace').annotate(
            total_duration=Sum('call_duration'),
        ).order_by('-total_duration')[:10]
    context = {'record': list(record)}
    return JsonResponse(context)


@permission_required("home.view_calls")
def get_call_counts_trace(request, id):
    try:
        client = Client.objects.get(client_id=id)
        device_id = client.client_device_id
        if client.client_device_id is None:
            return JsonResponse({'error_message': 'Client Doesn\'t Have Device Id'}, status=404)
    except Client.DoesNotExist:
        return JsonResponse({'error_message': 'No Client'}, status=404)
    time_type_result = get_time_type(request, device_id)
    # if isinstance(time_type_result, JsonResponse):
    #     return time_type_result
    start_time, end_time, time_type = time_type_result
    # if time_type not in ['0','1','2']:
    #     return JsonResponse({'error_message': 'Invalid timetype'}, status=400)
    call_type = request.GET.get('call_type')
    result = Calls.objects.filter(device_id=device_id, timestamp__range=[start_time, end_time])
    if call_type is None:
        top10 = result.values('trace').annotate(
            combined_counts=Count('trace'),
        ).order_by('-combined_counts')[:10]
        top10_trace_list = [i['trace'] for i in top10]
        temp_record = result.values('call_type', 'trace').annotate(
            counts=Count('call_type'),
        )
        record = temp_record.filter(trace__in=top10_trace_list)
    else:
        if call_type not in ['1', '2', '3']:
            return JsonResponse({'error_message': 'Invalid call type'}, status=400)
        record = result.filter(call_type=call_type).values('call_type', 'trace').annotate(
            counts=Count('call_type'),
        ).order_by('-counts')[:10]
    context = {'record': list(record)}
    return JsonResponse(context)


@permission_required("home.view_messages")
def get_sms_counts_time(request, id):
    try:
        client = Client.objects.get(client_id=id)
        device_id = client.client_device_id
        if client.client_device_id is None:
            return JsonResponse({'error_message': 'Client Doesn\'t Have Device Id'}, status=404)
    except Client.DoesNotExist:
        return JsonResponse({'error_message': 'No Client'}, status=404)
    time_type_result = get_time_type(request, device_id)
    if isinstance(time_type_result, JsonResponse):
        return time_type_result
    start_time, end_time, time_type = time_type_result
    if time_type not in ['0','1','2']:
        return JsonResponse({'error_message': 'Invalid timetype'}, status=400)
    result = Messages.objects.filter(device_id=device_id, timestamp__range=[start_time, end_time]).annotate(
        date=TruncDay(
            Func(
                F('timestamp') / 1000,
                function='from_unixtime',
                output_field=DateField(),
            ),
        )
    )
    if time_type == '0':
        if (datetime.fromtimestamp(end_time / 1000.0) - datetime.fromtimestamp(start_time / 1000.0)).days + 1 > 14:
            return JsonResponse({'error_message': 'Invalid time range'}, status=400)
        result = result.annotate(
            timestamp_to_date=TruncDay(
                Func(
                    F('timestamp') / 1000,
                    function='from_unixtime',
                    output_field=DateField(),
                ),
            ),
        )
    elif time_type == '1':
        e = datetime.fromtimestamp(end_time / 1000.0)
        s = datetime.fromtimestamp(start_time / 1000.0)
        if (e.year - s.year) * 12 + (e.month - s.month) + 1 > 12:
            return JsonResponse({'error_message': 'Invalid time range'}, status=400)
        result = result.annotate(
            timestamp_to_date=TruncMonth(
                Func(
                    F('timestamp') / 1000,
                    function='from_unixtime',
                    output_field=DateField(),
                ),
            ),
        )
    elif time_type == '2':
        e = datetime.fromtimestamp(end_time / 1000.0)
        s = datetime.fromtimestamp(start_time / 1000.0)
        if e.year - s.year + 1 > 12:
            return JsonResponse({'error_message': 'Invalid time range'}, status=400)
        result = result.annotate(
            timestamp_to_date=TruncYear(
                Func(
                    F('timestamp') / 1000,
                    function='from_unixtime',
                    output_field=DateField(),
                ),
            ),
        )
    record = result.values('message_type', 'timestamp_to_date').annotate(
        counts=Count('message_type'),
        min_time=Min('date'),
        max_time=Max('date')
    ).order_by('timestamp_to_date')
    context = {'record': list(record)}
    return JsonResponse(context)


@permission_required("home.view_messages")
def get_sms_counts_trace(request, id):
    try:
        client = Client.objects.get(client_id=id)
        device_id = client.client_device_id
        if client.client_device_id is None:
            return JsonResponse({'error_message': 'Client Doesn\'t Have Device Id'}, status=404)
    except Client.DoesNotExist:
        return JsonResponse({'error_message': 'No Client'}, status=404)
    time_type_result = get_time_type(request, device_id)
    # if isinstance(time_type_result, JsonResponse):
    #     return time_type_result
    start_time, end_time, time_type = time_type_result
    # if time_type not in ['0','1','2']:
    #     return JsonResponse({'error_message': 'Invalid timetype'}, status=400)
    message_type = request.GET.get('message_type')
    result = Messages.objects.filter(device_id=device_id, timestamp__range=[start_time, end_time])
    if message_type is None:
        top10 = result.values('trace').annotate(
            combined_counts=Count('trace'),
        ).order_by('-combined_counts')[:10]
        top10_trace_list = [i['trace'] for i in top10]
        temp_record = result.values('message_type', 'trace').annotate(
            counts=Count('message_type'),
        )
        record = temp_record.filter(trace__in=top10_trace_list)
    else:
        if message_type not in ['1', '2']:
            return JsonResponse({'error_message': 'Invalid message type'}, status=400)
        record = result.filter(message_type=message_type).values('message_type', 'trace').annotate(
            counts=Count('message_type'),
        ).order_by('-counts')[:10]
    context = {'record': list(record)}
    return JsonResponse(context)


@permission_required("home.view_client")
def get_all_clients(request, clinician_id):
    clinician = User.objects.get(id=clinician_id)
    client_list = Client.objects.filter(clinician_id=clinician).values('client_id', 'client_name',
                                                                          'client_first_name', 'client_last_name',
                                                                          'client_gender')
    items_per_page = 5
    paginator = Paginator(client_list, items_per_page)
    page_number = request.GET.get('page')

    try:
        if page_number is None:
            page_number = 1
        clients_page = paginator.page(page_number)
    except EmptyPage:
        # Handle the case when the requested page doesn't exist
        clients_page = paginator.page(1)  # Return the first page

    client_list = list(clients_page)

    context = {
        'client_list': list(client_list),
        'total_pages': paginator.num_pages
    }
    return JsonResponse(context)


@permission_required("home.view_client")
def get_client_by_id(request, client_id):
    client_info = Client.objects.filter(client_id=client_id).values('client_id', 'client_name', 'client_gender',
                                                                    'client_birthday', 'client_title',
                                                                    'client_first_name', 'client_last_name',
                                                                    'client_facebook_id', 'client_twitter_id',
                                                                    'client_device_id')
    return JsonResponse(list(client_info), safe=False)


@permission_required("home.view_client")
def get_client_by_name(request, clinician_id, client_name):
    clinician = User.objects.get(id=clinician_id)
    client_list = Client.objects.filter(clinician_id=clinician).values('client_id',
                                                                          'client_name',
                                                                          'client_first_name',
                                                                          'client_last_name',
                                                                          'client_gender')
    name_clients = client_list.filter(client_name=client_name)
    return JsonResponse(list(name_clients), safe=False)


@permission_required("home.add_client")
def add_client(request, clinician_id):
    try:
        clinician = User.objects.get(id=clinician_id)
        new_client = Client(
            clinician_id=clinician,
            client_name=request.POST.get('client_name'),
            client_gender=request.POST.get('client_gender'),
            client_birthday=request.POST.get('client_birthday'),
            client_title=request.POST.get('client_title'),
            client_first_name=request.POST.get('client_first_name'),
            client_last_name=request.POST.get('client_last_name'),
            client_facebook_id=request.POST.get('client_facebook_id'),
            client_twitter_id=request.POST.get('client_twitter_id'),
            client_device_id=request.POST.get('client_device_id')
        )


        new_client.save()
        return JsonResponse({'message': 'Client added successfully'})

    except Exception as e:
        return JsonResponse({'error_message': str(e)}, status=400)


@permission_required("home.delete_client")
def delete_client(request, client_id):
    try:
        client = Client.objects.get(pk=client_id)
        client.delete()

        return JsonResponse({'message': 'Client deleted successfully'})
    except Exception as e:
        return JsonResponse({'error_message': str(e)}, status=400)


@permission_required("home.change_client")
def update_client(request, client_id):
    try:
        client = Client.objects.get(pk=client_id)

        # client.client_name = request.POST.get('client_name')
        client.client_gender = request.POST.get('client_gender')
        client.client_birthday = request.POST.get('client_birthday')
        client.client_title = request.POST.get('client_title')
        client.client_first_name = request.POST.get('client_first_name')
        client.client_last_name = request.POST.get('client_last_name')
        client.client_facebook_id = request.POST.get('client_facebook_id')
        client.client_twitter_id = request.POST.get('client_twitter_id')
        client.client_device_id = request.POST.get('client_device_id')

        client.save()

        return JsonResponse({'message': 'Client updated successfully'})

    except Exception as e:
        return JsonResponse({'error_message': str(e)}, status=400)


def view_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.has_perm('auth.view_user'):
                return redirect('/admin/auth/user/')
            else:
                return redirect('/homePage')
            # username = request.POST['username']
            # password = request.POST['password']
            # user = authenticate(request, username=username, password=password)
            # if user is not None:
            #     login(request, user)
            #     if user.has_perm('auth.view_user'):
            #         return redirect('/admin/auth/user/')
            #     else:
            #         return redirect('/homePage')
            # else:
            #     form.non_field_errors = ["Incorrect username or password"]
            #     return render(request, 'views/Login/index.html', {'form': form})
        else:
            # form.non_field_errors = ["Invalid username or password"]
            return render(request, 'views/Login/index.html', {'form': form})
    else:
        return render(request, 'views/Login/index.html', {'form': AuthenticationForm()})


def view_logout(request):
    if (request.user.is_authenticated):
        logout(request)
    return redirect('view_login')


def dataAnalysis(request):
    if (request.user.is_authenticated):
        return render(request, 'views/dataAnalysis/index.html')
    else:
        return redirect('view_login')


def homePage(request):
    if (request.user.is_authenticated):
        return render(request, 'views/homePage/index.html')
    else:
        return redirect('view_login')


def viewClient(request):
    if (request.user.is_authenticated):
        return render(request, 'views/viewClient/index.html')
    else:
        return redirect('view_login')


def addClient(request):
    if (request.user.is_authenticated):
        return render(request, 'views/addClient/index.html')
    else:
        return redirect('view_login')


def call_data(request):
    return render(request, 'views/dataAnalysis/call_data.html')


def sms_data(request):
    return render(request, 'views/dataAnalysis/sms_data.html')