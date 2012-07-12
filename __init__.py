from flask import Flask, render_template
import boto

app = Flask(__name__)

iam = boto.connect_iam()
@app.route("/")
def index():
    return "Hello World!!"

@app.route("/ec2/")
@app.route("/ec2/<region>")
def ec2(region=None):

    il = [{'id':1, 'name':'i-ed6932ed'}, {'id':2,'name': 'i-ed6932ef' }]    
#    if region not None:
#        con = boto.connect_ec2(region=region)
#        instance_list = [{
#            'id': i.id,
#            'type': i.instance_type,
#            '':i.public_dns_name } for i in r.instances for r in con.get_all_instances()]


    return render_template('ec2.html', region=region,il=il)

@app.route("/r53/")
@app.route("/r53/<zone_id>")
def route53(zone_id=None):
    r53 = boto.connect_route53()
    if zone_id != None:
        rl = r53.get_all_rrsets(zone_id)
        rr = [{
            'type': r.type,
            'name': r.name,
            'ttl': r.ttl,
            'content': r.to_print()
            } for r in rl]

        return render_template('r53.html', zone_id=zone_id,rr=rr)

    else:
        hl = r53.get_all_hosted_zones()
        hzl = [{
            'id': hz['Id'].split("/")[-1],
            'name': hz['Name'],
            'count': hz['ResourceRecordSetCount']
            } for hz in hl['ListHostedZonesResponse']['HostedZones']]

        return render_template('r53.html', hzl=hzl)

@app.route("/iam/group/")
@app.route("/iam/group/<group_name>")
def IamGroup(group_name=None):
    if group_name == None:
        ''' http://example.com/iam/group '''
        gr = iam.get_all_groups()
        gl = [{
            'id': g.group_id,
            'name': g.group_name,
            'arn': g.arn,
            'created': g.create_date
            } for g in gr['list_groups_response']['list_groups_result']['groups']]

        return render_template('iamGroup.html', gl=gl)
    elif group_name != None:
        ''' http://example.com/iam/group/<group_name> '''
        gr = iam.get_group(group_name)
        group = gr['get_group_response']['get_group_result']['group']
        gd = {'id':group.group_id,
                'name':group.group_name,
                'created':group.create_date,
                'arn':group.arn}
        ul = gr['get_group_response']['get_group_result']['users']
        users = [{
            'id':u.user_id,
            'name':u.user_name,
            'arn':u.arn,
            'created':u.create_date
            } for u in ul]

        return render_template('iamGroup.html', gd=gd, users=users)

@app.route('/iam/user/')
@app.route("/iam/user/<user_name>")
def IamUser(user_name=None):

    if user_name == None:
        ''' http://example.com/iam/user '''
        ul = iam.get_all_users()

        return render_template('iamUser.html')
    elif user_name != None:
        ''' http://example.com/iam/user/<user_name> '''
        ud = iam.get_user(user_name)

        return render_template('iamUser.html')

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8834)

