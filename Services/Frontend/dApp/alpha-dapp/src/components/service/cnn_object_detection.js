import React from 'react';
import { Icon, Button, Upload } from 'antd';

class CNN_ObjectDetection extends React.Component {

    constructor(props) {
        super(props);

        this.submitAction = this.submitAction.bind(this);
        this.state = {
            fileUploaded: false,
            file: undefined,
            fileReader: undefined,

            method: 'detect',

            model_options: [
                {
                    name: 'Select Model',
                    value: null,
                },
                {
                    name: 'Not Available',
                    value: 'yolov3',
                },
                {
                    name: 'yolov3',
                    value: 'yolov3',
                },
            ],
            model_value: 'yolov3',

            confidence_options: [
                {
                    name: 'Select Confidence',
                    value: null,
                },
                {
                    name: '1%',
                    value: '0.01',
                },
                {
                    name: '10%',
                    value: '0.10',
                },
                {
                    name: '25%',
                    value: '0.25',
                },
                {
                    name: '50%',
                    value: '0.50',
                },
                {
                    name: '75%',
                    value: '0.75',
                },
                {
                    name: '90%',
                    value: '0.90',
                },
            ],
            confidence_value: '0.50',
        };

        this.ConfidencehandleChange = this.ConfidencehandleChange.bind(this);
        this.ModelhandleChange = this.ModelhandleChange.bind(this);

    }

    isComplete() {
        if (this.props.jobResult === undefined)
            return false;
        else {
            return true;
        }
    }

    processFile(file) {
        let reader = new FileReader();

        reader.onload = (e => {
            this.setState({
                fileUploaded: true,
                file: file,
                fileReader: reader,
            });
        });

        reader.readAsDataURL(file);
    }

    submitAction() {
        this.props.showModalCallback(this.props.callModal);
        this.props.callApiCallback(this.state.method, {
            confidence: this.state.confidence_value,
            model: this.state.model_value,
            img_path: this.state.fileReader.result.split(',')[1],
        });
    }

    ConfidencehandleChange(event) {
        this.setState({ confidence_value: event.target.value });
    };

    ModelhandleChange(event) {
        this.setState({ model_value: event.target.value });
    };

    renderForm() {
        return (
            <React.Fragment>
                <div>
                    <React.Fragment>
                        <div>
                            <table style={{ width: 30 }}>
                                <tbody>
                                    <tr>
                                        <td>Model:</td>
                                        <td>
                                            <select onChange={this.ModelhandleChange} value={this.state.model_value}>
                                                {this.state.model_options.map(item => (
                                                    <option key={item.value} value={item.value}>
                                                        {item.name}
                                                    </option>
                                                ))}
                                            </select>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>Confidence:</td>
                                        <td>
                                            <select onChange={this.ConfidencehandleChange} value={this.state.confidence_value}>
                                                {this.state.confidence_options.map(item => (
                                                    <option key={item.value} value={item.value}>
                                                        {item.name}
                                                    </option>
                                                ))}
                                            </select>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </React.Fragment>
                    {
                        !this.state.fileUploaded &&
                        <React.Fragment>
                            <br />
                            <br />
                            <Upload.Dragger name="file" accept=".jpg,.jpeg,.png" beforeUpload={(file) => { this.processFile(file); return false; }} >
                                <p className="ant-upload-drag-icon">
                                    <Icon type="inbox" />
                                </p>
                                <p className="ant-upload-text">Click for file-chooser dialog or drag a file to this area to be analyzed.</p>
                            </Upload.Dragger>
                        </React.Fragment>
                    }
                    <table><tbody>
                        <tr>
                            <td><b>File:</b></td>
                            <td>{this.state.file ? `${this.state.file.name}` : '(not uploaded)'}</td>
                        </tr>
                    </tbody>
                    </table>

                    <br />
                    <br />
                    {
                        this.state.fileUploaded &&
                        <img src={this.state.fileReader.result} />
                    }
                    <br />
                    <br />
                    <Button type="primary" onClick={() => { this.submitAction(); }} disabled={!this.state.fileUploaded} >Call Agent API</Button>
                </div>
            </React.Fragment >
        )
    }

    renderComplete() {
        let jsonResult = this.props.jobResult['result'];
        let delta_time = jsonResult['delta_time'];
        if (delta_time === undefined) delta_time = '-1';
        let imageBase64 = jsonResult['img_base64'];
        if (imageBase64 === undefined) imageBase64 = { '-1': jsonResult };

        return (
            <div>
                <div>
                    <img src={"data:image/jpg;base64," + imageBase64} />
                </div>
                <div>Execution time: {delta_time}s</div>
            </div>
        );
    }

    renderDescription() {
        return (
            <div>
                <p>
                    A service that uses CNN to detect objects in images.
                </p>
            </div>
        )
    }

    render() {
        if (this.isComplete())
            return (
                <div>
                    {this.renderDescription()}
                    {this.renderComplete()}
                </div>
            );
        else
            return (
                <div>
                    {this.renderDescription()}
                    {this.renderForm()}
                </div>
            )
    }
}

class Json2List extends React.Component {
    render() {
        return <li>{this.props.label + " - " + this.props.value}</li>;
    }
}

export default CNN_ObjectDetection;