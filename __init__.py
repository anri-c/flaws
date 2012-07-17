# -*- coding: utf-8 -*-
from flask import Flask, render_template
import boto
app = Flask(__name__)


@app.route("/")
def index():
    '''
    http://localhost/
    show main menu
    '''
    return render_template('index.html')


''' EC2 '''
@app.route("/ec2/region/")
@app.route("/ec2/region/<region>")
def ec2Region(region=None):
    import boto.ec2
    if region == None:
        '''
        http://localhost/ec2/region/
        get all available regions ec2
        '''
        region_list = [{
            'name': region.name,
            'endpoint':region.endpoint
            } for region in boto.ec2.regions()]

        return render_template('ec2/RegionIndex.html',
                region_list=region_list)

    else:
        ''' http://localhost/ec2/region/<region> '''
        con = boto.ec2.connect_to_region(region)
        instance_list = []
        for r in con.get_all_instances():
            for i in r.instances:
                instance_list.append({
                    'id':i.id,
                    'type':i.instance_type,
                    'pub_name': i.public_dns_name,
                    'pri_name': i.private_dns_name,
                    'vpc': i.vpc_id
                    })

        return render_template('ec2/RegionView.html',
                region=region, il=instance_list)

@app.route("/ec2/instance/")
@app.route("/ec2/instance/<instance_id>")
def ec2Instance(instance_id=None):
    import boto.ec2
    if instance_id == None:
        pass
    '''  '''


''' Autoscaling '''
@app.route("/ec2/autoscale/")
@app.route("/ec2/autoscale/<region>")
def asRegion(region=None):
    import boto.ec2.autoscale
    if region == None:
        '''
        http://localhost/ec2/autoscale 
        get all available regions for autoscaling
        '''
        region_list = [{
            'name': region.name,
            'endopoint':region.endpoint
            } for region in boto.ec2.autoscale.regions()]

        return render_template('as/RegionIndex.html',
                region_list=region_list)
    else:
        con = boto.ec2.autoscale.connect_to_region(region)
        con.get_all_groups()
        return render_template('as/RegionView.html')

''' RDS '''
@app.route("/rds/region/")
@app.route("/rds/region/<region>")
def rdsRegion(region=None):
    import boto.rds
    if region == None:
        '''
        http://localhost/rds/region/
        get all available regions for rds
        '''
        con = boto.rds.regions()
        region_list =[{
            'name': region.name,
            'endpoint':region.endpoint
            } for region in boto.rds.regions()]

        return render_template('rds/RegionIndex.html',
                region_list=region_list)

    else:
        con = boto.rds.connect_to_region(region)
        instance_list = [{
            'id':r.id,
            'type':r.instance_class,
            'engine':r.engine,
            'db':r.DBName
            }for r in con.get_all_dbinstances()]

        return render_template('rds/RegionView.html',
                region=region, instance_list=instance_list)





''' VPC '''
@app.route("/vpc/")
@app.route("/vpc/region/<region>")
def VirtualPrivateCloud(region=None):
    con = boto.connect_vpc()
    vpc_list = [{
        'id': vpc.id,
        'cidr': vpc.cidr_block,
        'state': vpc.state,
        'dhcp': vpc.dhcp_options_id
        } for vpc in con.get_all_vpcs()]


    return 


'''  No Region Start '''

''' Route 53 '''
@app.route("/r53/")
@app.route("/r53/<zone_id>")
def Route53(zone_id=None):
    con = boto.connect_route53()
    if zone_id != None:
        ''' http://localhost/r53/<zone_id>
        get all rrset specified zone id '''
        rl = con.get_all_rrsets(zone_id)
        rr = [{
            'type': r.type,
            'name': r.name,
            'ttl': r.ttl,
            'content': r.to_print()
            } for r in rl]

        return render_template('r53/ZoneView.html',
                zone_id=zone_id, rr=rr)

    else:
        ''' http://localhost/r53/ 
        get all hosted zone '''
        hl = con.get_all_hosted_zones()
        hzl = [{
            'id': hz['Id'].split("/")[-1],
            'name': hz['Name'],
            'count': hz['ResourceRecordSetCount']
            } for hz in hl['ListHostedZonesResponse']['HostedZones']]

        return render_template('r53/ZoneIndex.html',
                hzl=hzl)

''' IAM '''
@app.route("/iam/group/")
@app.route("/iam/group/<group_name>")
def IamGroup(group_name=None):
    con = boto.connect_iam()
    if group_name == None:
        ''' http://localhost/iam/group '''
        gr = con.get_all_groups()
        gl = [{
            'id': g.group_id,
            'name': g.group_name,
            'arn': g.arn,
            'created': g.create_date
            } for g in gr['list_groups_response']['list_groups_result']['groups']]

        return render_template('iam/GroupIndex.html',
                gl=gl)

    elif group_name != None:
        ''' http://localhost/iam/group/<group_name> '''
        gr = con.get_group(group_name)
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

        return render_template('iam/GroupView.html',
                gd=gd, users=users)

@app.route('/iam/user/')
@app.route("/iam/user/<user_name>")
def IamUser(user_name=None):
    con = boto.connect_iam()

    if user_name == None:
        ''' http://localhost/iam/user 
        get all IAM user '''
        ul = con.get_all_users()
        users = ul['list_users_response']['list_users_result']['users']
        user_list = [{
                'id': user.user_id,
                'name': user.user_name,
                'arn': user.arn,
                'created': user.create_date
                } for user in users ]

        return render_template('iam/UserIndex.html',
                user_list=user_list)

    elif user_name != None:
        ''' http://localhost/iam/user/<user_name> '''

        ''' get specified user detail '''
        ud = con.get_user(user_name)
        user = ud['get_user_response']['get_user_result']['user']

        ''' get all groups for specified user '''
        ug = con.get_groups_for_user(user_name)
        groups = ug['list_groups_for_user_response']['list_groups_for_user_result']['groups']
        group_list = [{
            'id': g.group_id,
            'name': g.group_name,
            'created': g.create_date
            } for g in groups ]

        ''' get all policies for specified user '''
        up = con.get_all_user_policies(user_name)
        policies = up['list_user_policies_response']['list_user_policies_result']

        return render_template('iam/UserView.html',
                user=user,group_list=group_list,policies=policies)

''' No Region End '''

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8834)

