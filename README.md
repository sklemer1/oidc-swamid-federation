# oidc-swamid-federation
A mini proof-of-concept OIDC federation using the Swamid/Amsterdam profile

This is an extremely simple *federation* with 2 entities. 
One RP and one OP.
As configured both entities belong to the same federations.
There are 2 federations/communities.
The federation is SWAMID and the community is EduGAIN. SWAMID being a member
of EduGAIN.

## Background

You should read the more detailed description that are part of the fedoidcmsg
 documentation. What I'll give you here will be a very short introduction.
 
The Swamid profile is built on the assumption that all entities in the 
federation are registered directly with the federation operator.

The Federation Operator (FO) is expected to run a metadata signing service 
(MDSS) that publishes the signed metadata statements for all entities within 
the federation.

The entities them self are not expected to keep signed metadata to be 
included in requests and/or responses.

## Installation

You will need pip to get everything installed. Best you do this in a virtenv.

If you don’t have pip, this will help you with that: https://pip.pypa.io/en/stable/installing/

Using pip you do:

``` bash
virtualenv -p python3 foobar
pip install atomicwrites
pip install git+https://github.com/openid/JWTConnect-Python-CryptoJWT.git@1eff9e5
pip install git+https://github.com/openid/JWTConnect-Python-OidcMsg.git@2c6bddc
pip install git+https://github.com/openid/JWTConnect-Python-OidcService.git@6bb00d6
pip install git+https://github.com/openid/JWTConnect-Python-OidcRP.git@85d09e4
pip install git+https://github.com/IdentityPython/oidcendpoint.git@37d107c
pip install git+https://github.com/rohe/oidc-op.git@71d293f
pip install git+https://github.com/IdentityPython/fedoidcmsg.git@d30107b
pip install git+https://github.com/IdentityPython/fedoidcservice.git@41f9fa6
pip install git+https://github.com/IdentityPython/fedoidcrp.git@700e443
pip install git+https://github.com/rohe/fed-oidc-endpoint.git@0c572b7
```
 
(if you feel adventurous you may omit the specific git revision "@FOOBAR")

!! You MUST get all of them !!

Once you have these packages you can get the Swamid mini fed setup.

``` bash
git clone https://github.com/sklemer1/oidc-swamid-federation.git
```

The steps below must be done in order.

### For the impatient

Do this once:

``` bash
cd oidc-swamid-federation
create_fo_bundle.py
cd MDSS
./create_sign_seq.py
cd ..
for i in RP OP; do
  cd $i
  ./enrollment_setup.py
  cd ..
done
cd MDSS
./enroll.py RP OP
```

Run the daemons

``` bash
cd RP
./rp.py -t -k conf &
cd ../OP
./server.py -t -k conf &
cd ../MDSS
./mdss.py -t config
```


Put this into cron (or run it regularly, at least once):
``` bash
./create_sign_seq.py
./metadata_importer.py
./processor.py
./signing_service.py
```

Point your Web browser at 
https://localhost:8080 and enter diana@localhost:8100 as you unique identifier and later diana/krall as username/password.

   
### Federation setup

You have to create the Federation Operators keys. This you do by running
create_fo_bundle.py . This script will create keys for the SWAMID and EduGAIN
federations. Placing the private keys in private/<FO name> and the public 
keys in public/<FO name>. It will also construct a FO bundle directory called 
*fo_bundle* . You **MUST** run the script from the root of the package.

### MDSS setup

The metadata signing service, run by SWAMID/SUNET, has to be initiated.
There are more steps that involves the MDSS but they will be taken care off as
they appear in the description below.

As mentioned above there are one federation and one federation community 
involved in this mini federation. They are each of the them described by 
their own configuration file (edugain_conf.json and swamid_conf.json).

Since the EduGain and Swamid keys where constructed by *create_fo_bundle.py* 
the configurations here only need to point out where the keys can be found.

The MDSS on the other hand needs it's own keys so the mdss_conf.json file 
will contain a specification of what type of signing keys the MDSS should have.

*create_sign_seq.py* is the script that will do the MDSS setup.
Apart from constructing the MDSS keys it will construct a set of metadata 
signing sequences. One for MDSS/SWAMID and the other for MDSS/SWAMID/EduGAIN.
One such set will be made for each of the different contexts where signed 
metadata statements can be used::

- Provider info discovery response  (discovery)
- Client registration               (registration)
- Client registration response      (response)


    $ cd MDSS
    $ ./create_sign_seq.py

Now that basic FO setup is done so let's bring in the entities. 

### Enrollment

To do enrollment each entity **MUST** construct a JSON document that looks 
like this:

    {
        "entity_id": "https://rp.example.com/metadata",
        "signing_keys": <JWKS>,
        "metadata_endpoint": "https://rp.example.com/metadata"
    } 

#### The RP enrollment    

For an RP the entity_id and the metadata_endpoint *should* be the same.

To construct this information from the configuration specification you can
use *enrollment_setup.py* which once run should have created the RP's
signing keys and written a file called *enrollment_info* that contains
the above mentions information. 

#### The OP enrollment

The entity_id for an OP *should* be the same as the issuer ID and since 
there are demands on the format/issuerID from the OIDC specification. Using 
the issuerID as the metadata_endpoint is probably not feasible.

Because of the above if you run *enrollment_setup.py* in the OP directory the
resulting *enrollment_info* will have the IssuerID as the entity_id but will
have a metadata_endpoint that is not the same as the entity_id.

If we assume that the RP and the OP administrators send there enrollment 
application to the FO the next thing that happens will be on the FOs side.

#### Adding entities to the FO

I don't have a separate FO directory, separate from the MDSS directory.
So everything the FO has will be in the same directory are the stuff needed 
by the MDSS.

Running *enroll.py* will basically copy the *enrollment_info* files from the 
entity (RP/OP) directories to a directory called *entities*.
It will also copy the MDSS public signing keys to a file called *mdss.jwks* 
in the entities directories.

    enroll.py RP OP
    
This process emulates the enrollment process that the FO has.
In reality it will definitely be more complex. I leave the implementation of
an enrollment process to the reader as an exercise.

Apart from wht *enroll.py* does one more thing has to be transmitted from
the FO to the entity and that is information about the MDSS.
In the configurations of the RP and the OP you can see these lines:

    'mdss_endpoint': 'https://localhost:8089',
    'mdss_owner': 'https://mdss.sunet.se',
    'mdss_keys': 'mdss.jwks',

If you had read the SWAMID profile documentation in the fedoidcmsg documentation
you would have seen that the endpoint the RP and the OP needs to know
about is the endpoint where they can find information about the collection of
signed metadata statements that the MDSS holds on the entity's behalf.
The path is given in the specification to be:

    /getsmscol/{context}/{entityID}
    
So only information about the leading part has to be transmitted.
The RP/OP will also need to know about thepublic part of the signing keys 
the MDSS uses and the entity ID of the MDSS.

#### Collecting metadata

Now the FO should collect metadata from the newly enrolled entities.
For this to work in this setting the RP and the OP needs to be running.
You can start them like this:

    $ cd RP
    $ ./rp.py -t -k conf &
    $ cd ../OP
    $ ./server.py -t -k conf &
   
And then run the collector

    $ cd MDSS
    $ ./metadata_importer.py
    
After having run this you should have 2 files in a directory called
entity_metadata. One called *https%3A%2F%2F127.0.0.1%3A8100*
and the other *https%3A%2F%2Flocalhost%3A8080%2Fmetadata*.

What *metadata_importer.py* did was look in the directory *entities* 
and for each file (entity) in that directory, based on the information
in the file, it fetched the metadata from the metadata_endpoint 
(in the form of a signed JWT) verified the signature and stored
the information in the JWT under the same file name as in the *entities*
directory in the directory *entity_metadata*.
 
#### Setting up the inbox

Now when we have the metadata for each entity there are a couple
of things the FO has to decide on. 

1. Are there any claims that should be removed/modified
2. Are there claims that should be added
3. In which contexts should this metadata be used.

After all those things has ben considered/applied then a signed
version of the metadata should be produced.

The three actions above have been modelled by the use of one
directory with some rules *process_rules* and one script *processor.py*.

The files (one per entity) in the *process_rules* directory all
follows the same pattern. And it looks like this:
  
    {
        "registration": {
            "https://edugain.org": {
                "federation_usage": "registration"},
            "https://swamid.sunet.se": {
                "federation_usage": "registration"}
        }
    }
        
The meaning of this is that this metadata can be used for
*registration* in the EduGAIN and SWAMID federations.
And one claim 'federation_usage' will be added to the metadata.

The *processor.py* will grab the metadata from the *entity_metadata*
directory, apply the rules and create a number of files in the
directory tree for processed metadata. The structure of this tree
is:

    {context}/{queue}/{federation_id}/{entity_id}
    
an example being

    registration/in/https%3A%2F%2Fswamid.sunet.se/https%3A%2F%2Flocalhost%3A8080%2Fmetadata
    
There are 2 queues (in/out). *processor.py* will write in the in
queue and the script *signing_service.py* will write to the out queue.

### Moving to the outbox

The next step in the chain is to construct signed metaddata statements 
for all the metadata instancecs that appear in the in queue.
*signing_service.py* will do this for you.
Just run it and it will populate the {context}/out directories.

### Running the MDSS

Now we have all the necessary data bases in order so we should be
able to run the MDSS. 

    $ ./mdss.py -t config

should do it.

## Testing the setup

If you've follow the instructions letter-by-letter you should
have the RP, the OP and the MDSS running by now.

Point your Web browser at 
https://localhost:8080 and enter diana@localhost:8100 as you unique identifier.

Using diana/krall as username/password you should end up with 
a web page with some information about Diana.
If not tell me what went wrong.
