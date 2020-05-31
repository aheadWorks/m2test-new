# docker-m2test

Image to run automatic tests against desired Magento 2 versions.

Supported tests type:

* unit to different  php versions
* static
* [EQP](https://github.com/magento/marketplace-eqp) 
* Validate marketplace package with [marketplace tools](https://github.com/magento/marketplace-tools)


## Usage

This image can be run agains folder with Magento 2 extension extension 

### Running unit and static tests

Run unit tests on extension folder against Magento 2.3 and PHP 7.2

```bash
docker run -v /local/folder/with/module:/data aheadworks/m2test:2.3-7.2 unit /data
```


Run static tests and collect test results in JUnit format
    
```bash
docker run -v /local/folder/with/module:/data -v /local/folder/for/results:/results aheadworks/m2test:2.2-7.1 static /data /results
```

Run unit tests and collect test results in JUnit format(result in `/local/folder/for/results/unit-tests.xml`

```bash
docker run -v /local/folder/with/module:/data -v /local/folder/for/results:/results aheadworks/m2test:2.2-7.1 unit /data /results/unit-tests.xml
```

### Running EQP(Magento coding standard) tests

Run tests from [Magento coding standard](https://github.com/magento/magento-coding-standard) versus your extension

```bash
docker run -v /local/folder/with/module:/data aheadworks/m2test:2.3-7.2 eqp --report=full /data
```

### Validating marketplace package

```bash
docker run -v /local/folder/with/module_zip:/data aheadworks/m2test validate_m2_package /data/module-name.zip
```

