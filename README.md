# clubbi_utils
Several helper functions, decorators and layers


## CLI

### Deploy lambda layer with versioning

Command:
```sh
clubbi_sls_utils_deploy_lambda_layer <STAGE>
```

#### Pre requirements
* node
* serverless 3.0

#### Setup
Make sure you have configured your aws credentials (usually it's already configured in the CI).

You must have a a `lambda_layer.yml` file with your serverless lambda layer definition with this output in
the resources section:
```yml
LambdaLayerRevision:
    Value: ${env:LOCK_HASH, ""}
```
The command will use the hash of the file `Pipfile.lock` as a deployment criteria, example: if the hash doesn't change, it won't redeploy.